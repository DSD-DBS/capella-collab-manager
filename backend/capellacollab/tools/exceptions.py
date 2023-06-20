# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import exception_handlers, status


class ToolVersionNotFoundError(Exception):
    def __init__(self, version_id: int):
        self.version_id = version_id


async def tool_version_not_found_exception_handler(
    request: fastapi.Request, exc: ToolVersionNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The tool version with id {exc.version_id} was not found."
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        ToolVersionNotFoundError, tool_version_not_found_exception_handler
    )
