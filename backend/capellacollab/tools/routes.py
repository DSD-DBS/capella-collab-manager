# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

import capellacollab.projects.toolmodels.crud as projects_models_crud
import capellacollab.settings.modelsources.t4c.crud as settings_t4c_crud
from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as users_models

from . import crud, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)


@router.get("", response_model=list[models.ToolBase])
def get_tools(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseTool]:
    return crud.get_tools(db)


@router.get("/default")
def get_default_tool() -> models.CreateTool:
    return models.CreateTool()


@router.get("/{tool_id}", response_model=models.ToolBase)
def get_tool_by_id(
    tool=fastapi.Depends(injectables.get_existing_tool),
) -> models.DatabaseTool:
    return tool


@router.post(
    "",
    response_model=models.ToolBase,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def create_tool(
    body: models.CreateTool, db: orm.Session = fastapi.Depends(database.get_db)
) -> models.DatabaseTool:
    """
    Creates a new tool, which can be used for tool models in projects and for
    sessions.

    To use this route, the user role `administrator` is required.
    """

    return crud.create_tool(db, body)


@router.put(
    "/{tool_id}",
    response_model=models.ToolBase,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def update_tool(
    body: models.CreateTool,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseTool:
    return crud.update_tool(db, tool, body)


@router.delete(
    "/{tool_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def delete_tool(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_dependency_exist(db, tool)
    crud.delete_tool(db, tool)


@router.get("/{tool_id}/versions", response_model=list[models.ToolVersionBase])
def get_tool_versions(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseVersion]:
    return crud.get_versions_for_tool_id(db, tool.id)


@router.get("/{tool_id}/versions/default")
def get_default_tool_version() -> models.CreateToolVersion:
    return models.CreateToolVersion()


@router.post(
    "/{tool_id}/versions",
    response_model=models.ToolVersionBase,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
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
    return crud.create_version(db, tool, body)


@router.get(
    "/{tool_id}/versions/{version_id}",
    response_model=models.ToolVersionBase,
)
def get_tool_version(
    version: models.DatabaseVersion = fastapi.Depends(
        injectables.get_existing_tool_version
    ),
) -> models.DatabaseVersion:
    return version


@router.put(
    "/{tool_id}/versions/{version_id}",
    response_model=models.ToolVersionBase,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
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
    return crud.update_version(db, version, body)


@router.delete(
    "/{tool_id}/versions/{version_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
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
    crud.delete_tool_version(db, version)


@router.get("/{tool_id}/natures", response_model=list[models.ToolNatureBase])
def get_tool_natures(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseNature]:
    return crud.get_natures_by_tool_id(db, tool.id)


@router.get("/{tool_id}/natures/default")
def get_default_tool_nature() -> models.CreateToolNature:
    return models.CreateToolNature()


@router.post(
    "/{tool_id}/natures",
    response_model=models.ToolNatureBase,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
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
    response_model=models.ToolNatureBase,
)
def get_tool_nature(
    nature: models.DatabaseNature = fastapi.Depends(
        injectables.get_existing_tool_nature
    ),
) -> models.DatabaseNature:
    return nature


@router.put(
    "/{tool_id}/natures/{nature_id}",
    response_model=models.ToolNatureBase,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
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
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
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
    HTTPException
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


def raise_when_tool_version_dependency_exist(
    db: orm.Session, version: models.DatabaseVersion
) -> None:
    """Search for tool version occurrences in project-models and T4C instances

    Raises
    ------
    HTTPException
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
    HTTPException
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
