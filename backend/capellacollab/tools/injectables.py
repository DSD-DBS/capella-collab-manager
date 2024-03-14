# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database

from . import crud, models


def get_existing_tool(
    tool_id: int, db: orm.Session = fastapi.Depends(database.get_db)
) -> models.DatabaseTool:
    if tool := crud.get_tool_by_id(db, tool_id):
        return tool

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The tool with the ID {tool_id} was not found.",
            "technical": f"Database returned 'None' when searching for the tool with id {tool_id}.",
        },
    )


def get_existing_tool_version(
    tool_id: int,
    version_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseVersion:
    if version := crud.get_version_by_version_and_tool_id(
        db, tool_id, version_id
    ):
        return version

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The version with tool_id {tool_id} and version_id {version_id} was not found.",
            "technical": f"Database returned 'None' when searching for the version with tool_id {tool_id} and version_id {version_id}.",
        },
    )


def get_existing_tool_nature(
    tool_id: int,
    nature_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseNature:
    if nature := crud.get_nature_for_tool(db, tool_id, nature_id):
        return nature

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The version with tool_id {tool_id} and nature_id {nature_id} was not found.",
            "technical": f"Database returned 'None' when searching for the version with tool_id {tool_id} and nature_id {nature_id}.",
        },
    )
