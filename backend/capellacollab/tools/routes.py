# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

import capellacollab.projects.toolmodels.crud as projects_models_crud
import capellacollab.settings.modelsources.t4c.instance.crud as settings_t4c_crud
from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core.logging import exceptions as logging_exceptions
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.Tool],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_tools(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseTool]:
    return crud.get_tools(db)


@router.get("/default")
def get_default_tool() -> models.CreateTool:
    return models.CreateTool()


@router.get(
    "/{tool_id}",
    response_model=models.Tool,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_tool_by_id(
    tool=fastapi.Depends(injectables.get_existing_tool),
) -> models.DatabaseTool:
    return tool


@router.post(
    "",
    response_model=models.Tool,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
        )
    ],
)
def create_tool(
    body: models.CreateTool, db: orm.Session = fastapi.Depends(database.get_db)
) -> models.DatabaseTool:
    """
    Creates a new tool, which can be used for tool models in projects and for
    sessions.
    """

    if (
        body.config.monitoring.logging.enabled
        and not config.k8s.promtail.loki_enabled
    ):
        raise logging_exceptions.GrafanaLokiDisabled()

    return crud.create_tool(db, body)


@router.put(
    "/{tool_id}",
    response_model=models.Tool,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def update_tool(
    body: models.CreateTool,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseTool:
    if (
        body.config.monitoring.logging.enabled
        and not config.k8s.promtail.loki_enabled
    ):
        raise logging_exceptions.GrafanaLokiDisabled()

    return crud.update_tool(db, tool, body)


@router.delete(
    "/{tool_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_tool(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_dependency_exist(db, tool)
    for version in tool.versions:
        remove_references_from_other_tool_versions(db, version)
    crud.delete_tool(db, tool)


@router.get(
    "/*/versions",
    response_model=list[models.ToolVersionWithTool],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_versions_for_all_tools(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseVersion]:
    return crud.get_versions(db)


@router.get(
    "/{tool_id}/versions",
    response_model=list[models.ToolVersion],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_tool_versions(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseVersion]:
    return crud.get_versions_for_tool_id(db, tool.id)


@router.get("/{_tool_id}/versions/default")
def get_default_tool_version(_tool_id: int) -> models.CreateToolVersion:
    return models.CreateToolVersion()


@router.post(
    "/{tool_id}/versions",
    response_model=models.ToolVersion,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
        )
    ],
)
def create_tool_version(
    body: models.CreateToolVersion,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseVersion:
    if crud.get_version_by_tool_id_version_name(db, tool.id, body.name):
        raise core_exceptions.ResourceAlreadyExistsError(
            "tool version", "name"
        )
    validate_compatible_tool_versions_exist(db, body)
    return crud.create_version(db, tool, body)


@router.get(
    "/{tool_id}/versions/{version_id}",
    response_model=models.ToolVersion,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_tool_version(
    version: models.DatabaseVersion = fastapi.Depends(
        injectables.get_existing_tool_version
    ),
) -> models.DatabaseVersion:
    return version


@router.put(
    "/{tool_id}/versions/{version_id}",
    response_model=models.ToolVersion,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def update_tool_version(
    body: models.CreateToolVersion,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    version: models.DatabaseVersion = fastapi.Depends(
        injectables.get_existing_tool_version
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseVersion:
    existing_version = crud.get_version_by_tool_id_version_name(
        db, tool.id, body.name
    )
    if existing_version and existing_version.id != version.id:
        raise core_exceptions.ResourceAlreadyExistsError(
            "tool version", "name"
        )
    validate_version_doesnt_reference_itself(version.id, body)
    validate_compatible_tool_versions_exist(db, body)
    return crud.update_version(db, version, body)


def validate_version_doesnt_reference_itself(
    id: int, tool_version: models.CreateToolVersion
):
    if id in tool_version.config.compatible_versions:
        raise exceptions.ReferencedOwnToolVersionError(tool_version_id=id)


@router.delete(
    "/{tool_id}/versions/{version_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_tool_version(
    version: models.DatabaseVersion = fastapi.Depends(
        injectables.get_existing_tool_version
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_version_dependency_exist(db, version)
    remove_references_from_other_tool_versions(db, version)
    crud.delete_tool_version(db, version)


@router.get(
    "/{tool_id}/natures",
    response_model=list[models.ToolNature],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_tool_natures(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseNature]:
    return crud.get_natures_by_tool_id(db, tool.id)


@router.get("/{_tool_id}/natures/default")
def get_default_tool_nature(_tool_id: int) -> models.CreateToolNature:
    return models.CreateToolNature()


@router.post(
    "/{tool_id}/natures",
    response_model=models.ToolNature,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
        )
    ],
)
def create_tool_nature(
    body: models.CreateToolNature,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseNature:
    if crud.get_nature_by_name(db, tool, body.name):
        raise core_exceptions.ResourceAlreadyExistsError("tool nature", "name")
    return crud.create_nature(db, tool, body.name)


@router.get(
    "/{tool_id}/natures/{nature_id}",
    response_model=models.ToolNature,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_tool_nature(
    nature: models.DatabaseNature = fastapi.Depends(
        injectables.get_existing_tool_nature
    ),
) -> models.DatabaseNature:
    return nature


@router.put(
    "/{tool_id}/natures/{nature_id}",
    response_model=models.ToolNature,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def update_tool_nature(
    body: models.CreateToolNature,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    nature: models.DatabaseNature = fastapi.Depends(
        injectables.get_existing_tool_nature
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseNature:
    existing_nature = crud.get_nature_by_name(db, tool, body.name)
    if existing_nature and existing_nature.id != nature.id:
        raise core_exceptions.ResourceAlreadyExistsError("tool nature", "name")
    return crud.update_nature(db, nature, body)


@router.delete(
    "/{tool_id}/natures/{nature_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        tools={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_tool_nature(
    nature: models.DatabaseNature = fastapi.Depends(
        injectables.get_existing_tool_nature
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_nature_dependency_exist(db, nature)
    crud.delete_nature(db, nature)


def raise_when_tool_dependency_exist(
    db: orm.Session, tool: models.DatabaseTool
) -> None:
    """Search for tool occurrences in project-models

    Raises
    ------
    core_exceptions.ExistingDependenciesError
        If there is a tool dependency left
    """

    dependencies: list[str] = []

    tool_models = projects_models_crud.get_models_by_tool(db, tool.id)
    dependencies.extend(
        f"Model '{model.name}' in project '{model.project.name}'"
        for model in tool_models
    )

    if dependencies:
        raise core_exceptions.ExistingDependenciesError(
            entity_name=tool.name,
            entity_type="tool",
            dependencies=dependencies,
        )


def remove_references_from_other_tool_versions(
    db: orm.Session, version_to_remove: models.DatabaseVersion
) -> None:
    """Remove the config.compatible_versions references from other tool versions"""

    for version_to_update in crud.get_versions(db):
        if (
            version_to_remove.id
            in version_to_update.config.compatible_versions
        ):
            crud.remove_tool_version_from_compatible_versions_config(
                db, version_to_update, version_to_remove
            )


def raise_when_tool_version_dependency_exist(
    db: orm.Session, version: models.DatabaseVersion
) -> None:
    """Search for tool version occurrences in project-models and T4C instances

    Raises
    ------
    core_exceptions.ExistingDependenciesError
        If there is a tool version dependency left
    """

    dependencies: list[str] = []

    # Search for occurrences in T4C Instances
    t4c_instances = settings_t4c_crud.get_t4c_instances_by_version(
        db, version.id
    )
    dependencies.extend(
        f"TeamForCapella instance '{instance.name}'"
        for instance in t4c_instances
    )

    # Search for occurrences in project-models
    version_models = projects_models_crud.get_models_by_version(db, version.id)
    dependencies.extend(
        f"Model '{model.name}' in project '{model.project.name}'"
        for model in version_models
    )

    if dependencies:
        raise core_exceptions.ExistingDependenciesError(
            entity_name=version.name,
            entity_type="version",
            dependencies=dependencies,
        )


def raise_when_tool_nature_dependency_exist(
    db: orm.Session, nature: models.DatabaseNature
) -> None:
    """Search for tool nature occurrences in project-models

    Raises
    ------
    core_exceptions.ExistingDependenciesError
        If there is a tool nature dependency left
    """

    dependencies: list[str] = []

    # Search for occurrences in project-models
    nature_models = projects_models_crud.get_models_by_nature(db, nature.id)
    dependencies.extend(
        f"Model '{model.name}' in project '{model.project.name}'"
        for model in nature_models
    )

    if dependencies:
        raise core_exceptions.ExistingDependenciesError(
            entity_name=nature.name,
            entity_type="nature",
            dependencies=dependencies,
        )


def validate_compatible_tool_versions_exist(
    db: orm.Session, body: models.CreateToolVersion
):
    """Validate that all compatible versions exist in the database"""
    for version_id in body.config.compatible_versions:
        if not crud.get_version_by_id(db, version_id):
            raise exceptions.ReferencedToolVersionNotFoundError(version_id)
