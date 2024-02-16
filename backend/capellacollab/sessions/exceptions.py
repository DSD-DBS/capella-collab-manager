# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status

from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models


@dataclasses.dataclass
class UnsupportedSessionTypeError(Exception):
    tool: tools_models.DatabaseTool
    session_type: sessions_models.SessionType


@dataclasses.dataclass
class ConflictingSessionError(Exception):
    tool: tools_models.DatabaseTool
    version: tools_models.DatabaseVersion
    session_type: sessions_models.SessionType


@dataclasses.dataclass
class ToolAndModelMismatchError(Exception):
    version: tools_models.DatabaseVersion
    model: toolmodels_models.DatabaseToolModel


@dataclasses.dataclass
class InvalidConnectionMethodIdentifierError(Exception):
    tool: tools_models.DatabaseTool
    connection_method_id: str


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


async def conflicting_session_handler(
    request: fastapi.Request, exc: ConflictingSessionError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "EXISTING_SESSION",
                "reason": (
                    f"You already have a '{exc.tool.name}' session with version '{exc.version.name}'. "
                    "Please terminate the existing session or reconnect to it."
                ),
            },
        ),
    )


async def tool_and_model_mismatch_handler(
    request: fastapi.Request, exc: ToolAndModelMismatchError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "MODEL_VERSION_MISMATCH",
                "reason": (
                    f"The model '{exc.model.name}' is not compatible with the tool {exc.version.tool.name} ({exc.version.name})'."
                ),
            },
        ),
    )


async def invalid_connection_method_identifier_handler(
    request: fastapi.Request, exc: InvalidConnectionMethodIdentifierError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "err_code": "CONNECTION_METHOD_UNKNOWN",
                "reason": (
                    f"The connection method with identifier '{exc.connection_method_id}' doesn't exist on the tool '{exc.tool.name}'."
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        UnsupportedSessionTypeError,
        unsupported_session_type_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        ConflictingSessionError,
        conflicting_session_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        ToolAndModelMismatchError,
        tool_and_model_mismatch_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        InvalidConnectionMethodIdentifierError,
        invalid_connection_method_identifier_handler,  # type: ignore[arg-type]
    )
