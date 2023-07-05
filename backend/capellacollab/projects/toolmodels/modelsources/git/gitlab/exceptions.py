# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import exception_handlers, status


class GitRepositoryFileNotFoundError(Exception):
    def __init__(self, filename: str):
        self.filename = filename


class GitInstanceAPIEndpointNotFoundError(Exception):
    pass


async def git_repository_file_not_found_handler(
    request: fastapi.Request, exc: GitRepositoryFileNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "err_code": "FILE_NOT_FOUND",
                "reason": (
                    f"No file with the name '{exc.filename}' found in the linked Git repository."
                    "Please contact your administrator.",
                ),
            },
        ),
    )


async def git_instance_api_endpoint_not_found_handler(
    request: fastapi.Request, _: GitInstanceAPIEndpointNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "err_code": "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED",
                "reason": (
                    "The used Git instance has no API endpoint defined.",
                    "Please contact your administrator.",
                ),
            },
        ),
    )


def register_exceptions(app: fastapi.FastAPI):
    app.add_exception_handler(
        GitRepositoryFileNotFoundError,
        git_repository_file_not_found_handler,
    )
    app.add_exception_handler(
        GitInstanceAPIEndpointNotFoundError,
        git_instance_api_endpoint_not_found_handler,
    )
