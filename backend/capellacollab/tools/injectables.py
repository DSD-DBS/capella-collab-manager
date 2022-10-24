# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy.exc
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.tools.models import Tool, Type, Version

from . import crud


def get_existing_tool(tool_id: int, db: Session = Depends(get_db)) -> Tool:
    try:
        return crud.get_tool_by_id(id_=tool_id, db=db)
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The tool with the ID {tool_id} was not found.",
                "technical": f"Database returned 'None' when searching for the tool with id {tool_id}.",
            },
        )


def get_exisiting_tool_version(
    tool_id: int, version_id: int, db: Session = Depends(get_db)
) -> Version:
    try:
        return crud.get_version_for_tool(tool_id, version_id, db)
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The version with tool_id {tool_id} and version_id {version_id} was not found.",
                "technical": f"Database returned 'None' when searching for the version with tool_id {tool_id} and version_id {version_id}.",
            },
        )


def get_exisiting_tool_type(
    tool_id: int, type_id: int, db: Session = Depends(get_db)
) -> Type:
    try:
        return crud.get_type_for_tool(tool_id, type_id, db)
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The version with tool_id {tool_id} and type_id {type_id} was not found.",
                "technical": f"Database returned 'None' when searching for the version with tool_id {tool_id} and type_id {type_id}.",
            },
        )
