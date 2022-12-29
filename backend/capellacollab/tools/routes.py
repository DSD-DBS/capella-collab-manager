# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.toolmodels.crud as projects_models_crud
import capellacollab.settings.modelsources.t4c.crud as settings_t4c_crud
from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.database import (
    get_db,
    patch_database_with_pydantic_object,
)
from capellacollab.tools import models
from capellacollab.tools.models import (
    CreateTool,
    CreateToolNature,
    CreateToolVersion,
    Nature,
    PatchToolDockerimage,
    Tool,
    ToolBase,
    ToolDockerimage,
    ToolNatureBase,
    ToolVersionBase,
    UpdateToolVersion,
    Version,
)
from capellacollab.users.models import Role

from . import crud, injectables
from .integrations.routes import router as router_integrations

router = APIRouter(
    dependencies=[Depends(RoleVerification(required_role=Role.USER))]
)


@router.get("", response_model=list[ToolBase])
def get_tools(db: Session = Depends(get_db)) -> list[Tool]:
    return crud.get_all_tools(db)


@router.get("/{tool_id}", response_model=ToolBase)
def get_tool_by_id(tool=Depends(injectables.get_existing_tool)) -> Tool:
    return tool


@router.post(
    "",
    response_model=ToolNatureBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool(body: CreateTool, db: Session = Depends(get_db)) -> Tool:
    return crud.create_tool(db, models.Tool(name=body.name))


@router.put(
    "/{tool_id}",
    response_model=ToolNatureBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def update_tool(
    body: CreateTool,
    tool: Tool = Depends(injectables.get_existing_tool),
    db: Session = Depends(get_db),
) -> Tool:
    return crud.update_tool(db, tool, body)


@router.delete(
    "/{tool_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_tool(
    tool: Tool = Depends(injectables.get_existing_tool),
    db: Session = Depends(get_db),
):
    if tool.id == 1:
        raise HTTPException(
            403,
            {
                "reason": "The tool 'Capella' can not be deleted.",
            },
        )
    try:
        crud.delete_tool(db, tool)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        find_tool_dependencies(db, tool)


def find_tool_dependencies(db: Session, tool: Tool) -> None:
    """Search for tool occurrences in project-models

    Raises
    ------
    HTTPException
        If there is a tool dependency left
    """

    dependencies = []
    for model in projects_models_crud.get_models_by_tool(tool.id, db):
        dependencies.append(
            f"Model '{model.name}' in project '{model.project.name}'"
        )

    for i in range(len(dependencies) - 1):
        dependencies[i] = dependencies[i] + ","

    if dependencies:
        raise HTTPException(
            409,
            {
                "reason": [
                    f"The tool '{tool.name}' can not be deleted. Please remove the following dependencies first:"
                ]
                + dependencies,
            },
        )


@router.get("/{tool_id}/versions", response_model=list[ToolVersionBase])
def get_tool_versions(
    tool_id: int, db: Session = Depends(get_db)
) -> list[Version]:
    return crud.get_tool_versions(db, tool_id)


@router.post(
    "/{tool_id}/versions",
    response_model=ToolVersionBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool_version(
    body: CreateToolVersion,
    tool: Tool = Depends(injectables.get_existing_tool),
    db: Session = Depends(get_db),
) -> Version:
    return crud.create_version(db, tool.id, body.name)


@router.patch(
    "/{tool_id}/versions/{version_id}",
    response_model=ToolVersionBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def patch_tool_version(
    body: UpdateToolVersion,
    version: Version = Depends(injectables.get_exisiting_tool_version),
    db: Session = Depends(get_db),
) -> Version:
    patch_database_with_pydantic_object(db, version, body)

    return crud.update_version(version, db)


@router.delete(
    "/{tool_id}/versions/{version_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_tool_version(
    version: Version = Depends(injectables.get_exisiting_tool_version),
    db: Session = Depends(get_db),
):
    try:
        crud.delete_tool_version(version, db)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        find_tool_version_dependencies(db, version)


def find_tool_version_dependencies(db: Session, version: Version) -> None:
    """Search for tool version occurrences in project-models and T4C instances

    Raises
    ------
    HTTPException
        If there is a tool version dependency left
    """

    dependencies = []
    # Search for occurrences in T4C Instances
    for instance in settings_t4c_crud.get_t4c_instances_by_version(
        version.id, db
    ):
        dependencies.append(f"TeamForCapella instance '{instance.name}'")

    # Search for occurrences in project-models
    for model in projects_models_crud.get_models_by_version(version.id, db):
        dependencies.append(
            f"Model '{model.name}' in project '{model.project.name}'"
        )

    for i in range(len(dependencies) - 1):
        dependencies[i] = dependencies[i] + ","

    if dependencies:
        raise HTTPException(
            409,
            {
                "reason": [
                    f"The version '{version.name}' can not be deleted. Please remove the following dependencies first:"
                ]
                + dependencies,
            },
        )


@router.get("/{tool_id}/natures", response_model=list[ToolNatureBase])
def get_tool_natures(
    tool_id: int, db: Session = Depends(get_db)
) -> list[Nature]:
    return crud.get_tool_natures(db, tool_id)


@router.post(
    "/{tool_id}/natures",
    response_model=ToolNatureBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool_nature(
    tool_id: int,
    body: CreateToolNature,
    db: Session = Depends(get_db),
) -> Nature:
    return crud.create_nature(db, tool_id, body.name)


@router.delete(
    "/{tool_id}/natures/{nature_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_tool_nature(
    nature: Nature = Depends(injectables.get_exisiting_tool_nature),
    db: Session = Depends(get_db),
):
    try:
        crud.delete_tool_nature(nature, db)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        find_tool_nature_dependencies(db, nature)


def find_tool_nature_dependencies(db: Session, nature: Nature) -> None:
    """Search for tool nature occurrences in project-models

    Raises
    ------
    HTTPException
        If there is a tool nature dependency left
    """

    dependencies = []
    # Search for occurrences in project-models
    for model in projects_models_crud.get_models_by_nature(nature.id, db):
        dependencies.append(
            f"Model '{model.name}' in project '{model.project.name}'"
        )

    for i in range(len(dependencies) - 1):
        dependencies[i] = dependencies[i] + ","

    if dependencies:
        raise HTTPException(
            409,
            {
                "reason": [
                    f"The nature '{nature.name}' can not be deleted. Please remove the following dependencies first:"
                ]
                + dependencies,
            },
        )


@router.get(
    "/{tool_id}/dockerimages",
    response_model=ToolDockerimage,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_dockerimages(
    tool: Tool = Depends(injectables.get_existing_tool),
) -> Tool:
    return tool


@router.put(
    "/{tool_id}/dockerimages",
    response_model=ToolDockerimage,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def update_dockerimages(
    body: PatchToolDockerimage,
    tool: Tool = Depends(injectables.get_existing_tool),
    db: Session = Depends(get_db),
) -> Tool:
    return crud.update_tool(db, tool, body)


router.include_router(router_integrations, prefix="/{tool_id}/integrations")
