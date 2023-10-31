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
    session_type: sessions_models.WorkspaceType


@dataclasses.dataclass
class MissingPrimaryGitModelError(Exception):
    model: toolmodels_models.DatabaseCapellaModel


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


async def missing_primary_git_model_error(
    request: fastapi.Request, exc: MissingPrimaryGitModelError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "MISSING_GIT_MODEL",
                "reason": (
                    f"The model {exc.model.name} doesn't support have a primary git model defined"
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
        MissingPrimaryGitModelError,
        missing_primary_git_model_error,
    )
