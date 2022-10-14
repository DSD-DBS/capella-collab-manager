# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.tools.models import ToolBase, ToolTypeBase, ToolVersionBase

from . import crud

router = APIRouter()


@router.get("/", tags=["Tools"], response_model=list[ToolBase])
def get_tools(db: Session = Depends(get_db)):
    return crud.get_all_tools(db)


@router.post(
    "",
    response_model=ToolTypeBase,
    dependencies=[Depends(verify_admin)],
)
def create_tool(body: CreateTool, db: Session = Depends(get_db)):
    return crud.create_tool(db, models.Tool(name=body.name))


@router.put(
    "/{tool_id}",
    response_model=ToolTypeBase,
    dependencies=[Depends(verify_admin)],
)
def update_tool(tool_id: int, body: CreateTool, db: Session = Depends(get_db)):
    tool = crud.get_tool_by_id(tool_id, db)
    return crud.update_tool(db, tool, body)


@router.get("/{tool_id}/versions", response_model=list[ToolVersionBase])
def get_tool_versions(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_versions(db, tool_id)


@router.get(
    "/{tool_id}/types", tags=["Tools"], response_model=list[ToolTypeBase]
)
def get_tool_types(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_types(db, tool_id)
