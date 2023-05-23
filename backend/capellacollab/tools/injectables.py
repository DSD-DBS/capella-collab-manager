# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.tools.models import Nature, Tool, Version

from . import crud


def get_existing_tool(tool_id: int, db: Session = Depends(get_db)) -> Tool:
    if tool := crud.get_tool_by_id(db, tool_id):
        return tool

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The tool with the ID {tool_id} was not found.",
            "technical": f"Database returned 'None' when searching for the tool with id {tool_id}.",
        },
    )


def get_exisiting_tool_version(
    tool_id: int, version_id: int, db: Session = Depends(get_db)
) -> Version:
    if version := crud.get_version_by_version_and_tool_id(
        db, tool_id, version_id
    ):
        return version

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The version with tool_id {tool_id} and version_id {version_id} was not found.",
            "technical": f"Database returned 'None' when searching for the version with tool_id {tool_id} and version_id {version_id}.",
        },
    )


def get_exisiting_tool_nature(
    tool_id: int, nature_id: int, db: Session = Depends(get_db)
) -> Nature:
    if nature := crud.get_nature_for_tool(db, tool_id, nature_id):
        return nature

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The version with tool_id {tool_id} and nature_id {nature_id} was not found.",
            "technical": f"Database returned 'None' when searching for the version with tool_id {tool_id} and nature_id {nature_id}.",
        },
    )
