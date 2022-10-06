# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import APIRouter, Depends
from requests import Session

from capellacollab.core.database import get_db
from capellacollab.tools.models import ToolBase, ToolVersionBase

from . import crud

router = APIRouter()


@router.get("/", response_model=list[ToolBase])
def get_tools(db: Session = Depends(get_db)):
    return crud.get_all_tools(db)


@router.get("/:tool_id/versions", response_model=list[ToolVersionBase])
def get_tool_versions(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_versions(db, tool_id)


@router.get("/:tool_id/types", response_model=list[ToolVersionBase])
def get_tool_types(tool_id: int, db: Session = Depends(get_db)):
    return crud.get_tool_types(db, tool_id)
