# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import exception_handlers, status


class TooManyOutStandingRequests(Exception):
    pass


async def too_many_outstanding_requests_handler(
    request: fastapi.Request, _: TooManyOutStandingRequests
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "err_code": "LOKI_TOO_MANY_OUTSTANDING_REQUESTS",
                "reason": "Too many outstanding requests. Please try again later.",
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        TooManyOutStandingRequests, too_many_outstanding_requests_handler  # type: ignore[arg-type]
    )
