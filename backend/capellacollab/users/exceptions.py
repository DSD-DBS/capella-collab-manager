# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status


@dataclasses.dataclass
class UserNotFoundError(Exception):
    username: str | None = None
    user_id: int | None = None


async def user_not_found_exception_handler(
    request: fastapi.Request, exc: UserNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "title": "User not found",
                "reason": f"The user '{exc.username or exc.user_id}' doesn't exist.",
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        UserNotFoundError, user_not_found_exception_handler  # type: ignore[arg-type]
    )
