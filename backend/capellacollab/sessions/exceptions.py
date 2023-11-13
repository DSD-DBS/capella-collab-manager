# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status

from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models


@dataclasses.dataclass
class UnsupportedSessionTypeError(Exception):
    tool: tools_models.DatabaseTool
    session_type: sessions_models.WorkspaceType


async def unsupported_session_type_handler(
    request: fastapi.Request, exc: UnsupportedSessionTypeError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "SESSION_TYPE_UNSUPPORTED",
                "reason": (
                    f"The tool {exc.tool.name} doesn't support the session type '{exc.session_type.value}'"
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        UnsupportedSessionTypeError,
        unsupported_session_type_handler,  # type: ignore[arg-type]
    )
