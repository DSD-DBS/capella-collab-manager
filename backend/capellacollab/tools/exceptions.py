# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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


class ToolImageNotFoundError(Exception):
    def __init__(self, tool_id: int, image_name: str):
        self.tool_id = tool_id
        self.image_name = image_name


async def tool_image_not_found_exception_handler(
    request: fastapi.Request, exc: ToolImageNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The tool with id {exc.tool_id} doesn't have a {exc.image_name} image."
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        ToolVersionNotFoundError, tool_version_not_found_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        ToolImageNotFoundError, tool_image_not_found_exception_handler  # type: ignore[arg-type]
    )
