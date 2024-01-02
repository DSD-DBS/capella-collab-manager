# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import exception_handlers, status


class VersionIdNotSetError(Exception):
    def __init__(self, toolmodel_id: int):
        self.toolmodel_id = toolmodel_id


async def version_id_not_set_exception_handler(
    request: fastapi.Request, exc: VersionIdNotSetError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "reason": f"The toolmodel with id {exc.toolmodel_id} does not have a version set."
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        VersionIdNotSetError, version_id_not_set_exception_handler  # type: ignore[arg-type]
    )
