# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.database import get_db
from capellacollab.tools import models
from capellacollab.tools.models import (
    CreateTool,
    PatchToolDockerimage,
    Tool,
    ToolBase,
    ToolDockerimage,
    ToolTypeBase,
    ToolVersionBase,
)
from capellacollab.users.models import Role

from . import crud

router = APIRouter()


def get_existing_tool(tool_id: str) -> Tool:
    tool = crud.get_tool_by_id(tool_id)
    if not tool:
        raise HTTPException(
            404,
            {
                "reason": f"The tool with the ID {tool_id} was not found.",
                "technical": f"Database returned 'None' when searching for the tool with id {tool_id}.",
            },
        )
    return tool


@router.get(
    "",
    response_model=list[ToolBase],
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tools(db: Session = Depends(get_db)):
    return crud.get_all_tools(db)


@router.get(
    "/{tool_id}",
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tool_by_id(tool=Depends(get_existing_tool)):
    return tool


@router.post(
    "",
    response_model=ToolTypeBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool(body: CreateTool, db: Session = Depends(get_db)):
    return crud.create_tool(db, models.Tool(name=body.name))


@router.put(
    "/{tool_id}",
    response_model=ToolTypeBase,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def update_tool(tool_id: int, body: CreateTool, db: Session = Depends(get_db)):
    tool = crud.get_tool_by_id(tool_id, db)
    return crud.update_tool(db, tool, body)


@router.delete(
    "/{tool_id}",
    response_model=list[ToolTypeBase],
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    crud.delete_tool(db, tool_id)
    return None


@router.get(
    "/{tool_id}/versions",
    response_model=list[ToolVersionBase],
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tool_versions(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_versions(db, tool_id)


@router.post(
    "/{tool_id}/versions",
    response_model=list[ToolVersionBase],
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool_version(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_versions(db, tool_id)


@router.get(
    "/{tool_id}/types",
    response_model=list[ToolTypeBase],
    dependencies=[Depends(RoleVerification(required_role=Role.USER))],
)
def get_tool_types(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_types(db, tool_id)


@router.post(
    "/{tool_id}/types",
    response_model=list[ToolTypeBase],
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def create_tool_type(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_types(db, tool_id)


@router.get(
    "/{tool_id}/dockerimages",
    response_model=ToolDockerimage,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def get_dockerimages(
    tool: Tool = Depends(get_existing_tool),
):
    return ToolDockerimage(
        persistent=tool.docker_image_template, readonly="FIXME"
    )


@router.put(
    "/{tool_id}/dockerimages",
    response_model=ToolDockerimage,
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
)
def update_dockerimages(
    body: PatchToolDockerimage,
    tool: Tool = Depends(get_existing_tool),
    db: Session = Depends(get_db),
):
    return crud.update_tool(db, tool, body)
