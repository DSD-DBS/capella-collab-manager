# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import sqlalchemy.exc
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import capellacollab.projects.capellamodels.crud as projects_models_crud
import capellacollab.settings.modelsources.t4c.crud as settings_t4c_crud
from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.database import get_db
from capellacollab.tools import models
from capellacollab.tools.models import (
    CreateTool,
    CreateToolType,
    CreateToolVersion,
    PatchToolDockerimage,
    Tool,
    ToolBase,
    ToolDockerimage,
    ToolTypeBase,
    ToolVersionBase,
    Type,
    UpdateToolVersion,
    Version,
)
from capellacollab.users.models import Role

from . import crud, injectables

router = APIRouter()


@router.get(
    "",
    response_model=list[ToolBase],
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tools(db: Session = Depends(get_db)) -> list[Tool]:
    return crud.get_all_tools(db)


@router.get(
    "/{tool_id}",
    response_model=ToolBase,
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tool_by_id(tool=Depends(injectables.get_existing_tool)) -> Tool:
    return tool


@router.post(
    "",
    response_model=ToolTypeBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool(body: CreateTool, db: Session = Depends(get_db)) -> Tool:
    return crud.create_tool(db, models.Tool(name=body.name))


@router.put(
    "/{tool_id}",
    response_model=ToolTypeBase,
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
) -> None:
    if tool.id == 1:
        raise HTTPException(
            403,
            {
                "reason": "The tool 'Capella' can not be deleted.",
            },
        )
    try:
        return crud.delete_tool(db, tool)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()

        dependencies = []
        # Search for occurrences in project-models
        for model in projects_models_crud.get_models_by_tool(tool.id, db):
            dependencies.append(
                f"Model '{model.name}' in project '{model.project.name}'"
            )

        for i in range(len(dependencies) - 1):
            dependencies[i] = dependencies[i] + ","

        raise HTTPException(
            409,
            {
                "reason": [
                    f"The tool '{tool.name}' can not be deleted. Please remove the following dependencies first:"
                ]
                + dependencies,
            },
        )


@router.get(
    "/{tool_id}/versions",
    response_model=list[ToolVersionBase],
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
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
    return crud.create_version(db, tool.id, body.name, False, False)


@router.patch(
    "/{tool_id}/versions/{version_id}",
    response_model=ToolVersionBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def patch_tool_version(
    body: UpdateToolVersion,
    version=Depends(injectables.get_exisiting_tool_version),
    db: Session = Depends(get_db),
) -> Version:
    for key, value in body.dict().items():
        if value is not None:
            version.__setattr__(key, value)

    return crud.update_version(version, db)


@router.delete(
    "/{tool_id}/versions/{version_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_tool_version(
    version=Depends(injectables.get_exisiting_tool_version),
    db: Session = Depends(get_db),
) -> None:
    try:
        return crud.delete_tool_version(version, db)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()

        dependencies = []
        # Search for occurrences in T4C Instances
        for instance in settings_t4c_crud.get_t4c_instances_by_version(
            version.id, db
        ):
            dependencies.append(f"TeamForCapella instance '{instance.name}'")

        # Search for occurrences in project-models
        for model in projects_models_crud.get_models_by_version(
            version.id, db
        ):
            dependencies.append(
                f"Model '{model.name}' in project '{model.project.name}'"
            )

        for i in range(len(dependencies) - 1):
            dependencies[i] = dependencies[i] + ","

        raise HTTPException(
            409,
            {
                "reason": [
                    f"The version '{version.name}' can not be deleted. Please remove the following dependencies first:"
                ]
                + dependencies,
            },
        )


@router.get(
    "/{tool_id}/types",
    response_model=list[ToolTypeBase],
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tool_types(tool_id: int, db: Session = Depends(get_db)) -> list[Type]:
    return crud.get_tool_types(db, tool_id)


@router.post(
    "/{tool_id}/types",
    response_model=ToolTypeBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool_type(
    tool_id: int,
    body: CreateToolType,
    db: Session = Depends(get_db),
) -> Type:
    return crud.create_type(db, tool_id, body.name)


@router.delete(
    "/{tool_id}/types/{type_id}",
    status_code=204,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_tool_type(
    type=Depends(injectables.get_exisiting_tool_type),
    db: Session = Depends(get_db),
) -> None:
    try:
        return crud.delete_tool_type(type, db)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()

        dependencies = []
        # Search for occurrences in project-models
        for model in projects_models_crud.get_models_by_type(type.id, db):
            dependencies.append(
                f"Model '{model.name}' in project '{model.project.name}'"
            )

        for i in range(len(dependencies) - 1):
            dependencies[i] = dependencies[i] + ","

        raise HTTPException(
            409,
            {
                "reason": [
                    f"The type '{type.name}' can not be deleted. Please remove the following dependencies first:"
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
