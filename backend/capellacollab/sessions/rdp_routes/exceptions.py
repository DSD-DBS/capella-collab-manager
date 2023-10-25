# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status


@dataclasses.dataclass
class SessionRouteAlreadyAvailable(Exception):
    pass


async def session_route_already_available_handler(
    request: fastapi.Request, _: SessionRouteAlreadyAvailable
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "err_code": "SESSION_ROUTE_ALREADY_AVAILABLE",
                "reason": (
                    "We do not support multiple session routes at the moment. "
                    "Please the existing route."
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        SessionRouteAlreadyAvailable,
        session_route_already_available_handler,
    )
