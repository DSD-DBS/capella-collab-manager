# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.crud as projects_models_crud
import capellacollab.settings.modelsources.t4c.crud as settings_t4c_crud
from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.tools.integrations import (
    routes as tools_integrations_routes,
)
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


@router.get("/{tool_id}", response_model=models.ToolBase)
def get_tool_by_id(
    tool=fastapi.Depends(injectables.get_existing_tool),
) -> models.DatabaseTool:
    return tool


@router.post(
    "",
    response_model=models.ToolNatureBase,
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
    return crud.create_tool_with_name(db, body.name)


@router.put(
    "/{tool_id}",
    response_model=models.ToolNatureBase,
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
    return crud.update_tool_name(db, tool, body.name)


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
    if tool.id == 1:
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "The tool 'Capella' cannot be deleted.",
            },
        )

    raise_when_tool_dependency_exist(db, tool)
    crud.delete_tool(db, tool)


@router.get("/{tool_id}/versions", response_model=list[models.ToolVersionBase])
def get_tool_versions(
    tool_id: int, db: orm.Session = fastapi.Depends(database.get_db)
) -> abc.Sequence[models.DatabaseVersion]:
    return crud.get_versions_for_tool_id(db, tool_id)


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
    return crud.create_version(db, tool, body.name)


@router.patch(
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
def patch_tool_version(
    body: models.UpdateToolVersion,
    version: models.DatabaseVersion = fastapi.Depends(
        injectables.get_exisiting_tool_version
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseVersion:
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
        injectables.get_exisiting_tool_version
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_version_dependency_exist(db, version)
    crud.delete_tool_version(db, version)


@router.get("/{tool_id}/natures", response_model=list[models.ToolNatureBase])
def get_tool_natures(
    tool_id: int, db: orm.Session = fastapi.Depends(database.get_db)
) -> abc.Sequence[models.DatabaseNature]:
    return crud.get_natures_by_tool_id(db, tool_id)


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
    return crud.create_nature(db, tool, body.name)


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
        injectables.get_exisiting_tool_nature
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_nature_dependency_exist(db, nature)
    crud.delete_nature(db, nature)


@router.get(
    "/{tool_id}/dockerimages",
    response_model=models.ToolDockerimage,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def get_dockerimages(
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
) -> models.DatabaseTool:
    return tool


@router.put(
    "/{tool_id}/dockerimages",
    response_model=models.ToolDockerimage,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def update_dockerimages(
    body: models.PatchToolDockerimage,
    tool: models.DatabaseTool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseTool:
    return crud.update_tool_dockerimages(db, tool, body)


router.include_router(
    tools_integrations_routes.router, prefix="/{tool_id}/integrations"
)


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
