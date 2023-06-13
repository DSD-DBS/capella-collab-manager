# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.crud as projects_models_crud
import capellacollab.settings.modelsources.t4c.crud as settings_t4c_crud
from capellacollab.core import database
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
) -> abc.Sequence[models.Tool]:
    return crud.get_tools(db)


@router.get("/{tool_id}", response_model=models.ToolBase)
def get_tool_by_id(
    tool=fastapi.Depends(injectables.get_existing_tool),
) -> models.Tool:
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
) -> models.Tool:
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
    tool: models.Tool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.Tool:
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
    tool: models.Tool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if tool.id == 1:
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": "The tool 'Capella' can not be deleted.",
            },
        )

    raise_when_tool_dependency_exist(db, tool)
    crud.delete_tool(db, tool)


@router.get("/{tool_id}/versions", response_model=list[models.ToolVersionBase])
def get_tool_versions(
    tool_id: int, db: orm.Session = fastapi.Depends(database.get_db)
) -> abc.Sequence[models.Version]:
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
    tool: models.Tool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.Version:
    return crud.create_version(db, tool.id, body.name)


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
    version: models.Version = fastapi.Depends(
        injectables.get_exisiting_tool_version
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.Version:
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
    version: models.Version = fastapi.Depends(
        injectables.get_exisiting_tool_version
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    raise_when_tool_version_dependency_exist(db, version)
    crud.delete_tool_version(db, version)


@router.get("/{tool_id}/natures", response_model=list[models.ToolNatureBase])
def get_tool_natures(
    tool_id: int, db: orm.Session = fastapi.Depends(database.get_db)
) -> abc.Sequence[models.Nature]:
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
    tool_id: int,
    body: models.CreateToolNature,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.Nature:
    return crud.create_nature(db, tool_id, body.name)


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
    nature: models.Nature = fastapi.Depends(
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
    tool: models.Tool = fastapi.Depends(injectables.get_existing_tool),
) -> models.Tool:
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
    tool: models.Tool = fastapi.Depends(injectables.get_existing_tool),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.Tool:
    return crud.update_tool_dockerimages(db, tool, body)


router.include_router(
    tools_integrations_routes.router, prefix="/{tool_id}/integrations"
)


def raise_when_tool_dependency_exist(
    db: orm.Session, tool: models.Tool
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

    raise_if_dependencies_exist(dependencies, tool.name, "tool")


def raise_when_tool_version_dependency_exist(
    db: orm.Session, version: models.Version
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

    raise_if_dependencies_exist(dependencies, version.name, "version")


def raise_when_tool_nature_dependency_exist(
    db: orm.Session, nature: models.Nature
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

    raise_if_dependencies_exist(dependencies, nature.name, "nature")


def raise_if_dependencies_exist(
    dependencies: list[str], entity_name: str, entity_type: str
) -> None:
    """Raise HTTPException if there are any dependencies.

    Parameters
    ----------
    dependencies : list[str]
        List of dependency descriptions
    entity_name : str
        Name of the entity with dependencies
    entity_type : str
        Type of the entity with dependencies
    """

    if dependencies:
        dependencies_str = ", ".join(dependencies)
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": [
                    f"The {entity_type} '{entity_name}' can not be deleted. Please remove the following dependencies first: {dependencies_str}"
                ]
            },
        )
