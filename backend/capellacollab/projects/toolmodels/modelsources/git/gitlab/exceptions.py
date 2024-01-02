# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status

from .. import exceptions as git_exceptions


class GitlabAccessDeniedError(git_exceptions.AccessDeniedError):
    pass


@dataclasses.dataclass
class GitlabProjectNotFoundError(git_exceptions.RepositoryNotFoundError):
    project_name: str


async def gitlab_access_denied_handler(
    request: fastapi.Request, _: GitlabAccessDeniedError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "err_code": "GITLAB_ACCESS_DENIED",
                "reason": (
                    "The registered token has not enough permissions to access the Gitlab API.",
                    "Access scope 'read_api' is required. Please contact your project lead.",
                ),
            },
        ),
    )


async def gitlab_project_not_found_handler(
    request: fastapi.Request, exc: GitlabProjectNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "err_code": "PROJECT_NOT_FOUND",
                "reason": (
                    "We couldn't find the project in your Gitlab instance.",
                    f"Please make sure that a project with the encoded name '{exc.project_name}' does exist.",
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        GitlabAccessDeniedError,
        gitlab_access_denied_handler,  # type: ignore[arg-type]
    )

    app.add_exception_handler(
        GitlabProjectNotFoundError,
        gitlab_project_not_found_handler,  # type: ignore[arg-type]
    )
