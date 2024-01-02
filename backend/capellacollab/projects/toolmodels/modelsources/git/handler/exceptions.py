# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status


@dataclasses.dataclass
class GitInstanceUnsupportedError(Exception):
    instance_name: str


class NoMatchingGitInstanceError(Exception):
    pass


async def git_instance_unsupported_handler(
    request: fastapi.Request, exc: GitInstanceUnsupportedError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "err_code": "GIT_INSTANCE_UNSUPPORTED",
                "reason": (
                    f"The Git instance '{exc.instance_name}' doesn't support the requested operation.",
                ),
            },
        ),
    )


async def no_matching_git_instance_handler(
    request: fastapi.Request, _: NoMatchingGitInstanceError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "err_code": "NO_MATCHING_GIT_INSTANCE",
                "reason": (
                    "No matching git instance was found for the primary git model.",
                    "Please contact your administrator.",
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        GitInstanceUnsupportedError,
        git_instance_unsupported_handler,  # type: ignore[arg-type]
    )

    app.add_exception_handler(
        NoMatchingGitInstanceError,
        no_matching_git_instance_handler,  # type: ignore[arg-type]
    )
