# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import dataclasses

import fastapi
from fastapi import exception_handlers, status


class AccessDeniedError(Exception):
    pass


class RepositoryNotFoundError(Exception):
    pass


@dataclasses.dataclass
class GitRepositoryFileNotFoundError(Exception):
    filename: str


class GitInstanceAPIEndpointNotFoundError(Exception):
    pass


@dataclasses.dataclass
class GitPipelineJobNotFoundError(Exception):
    job_name: str


@dataclasses.dataclass
class GitPipelineJobFailedError(Exception):
    job_name: str


@dataclasses.dataclass
class GitPipelineJobUnknownStateError(Exception):
    job_name: str
    state: str


class GithubArtifactExpiredError(Exception):
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "err_code": "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED",
                "reason": (
                    "The used Git instance has no API endpoint defined.",
                    "Please contact your administrator.",
                ),
            },
        ),
    )


async def git_pipeline_job_not_found_handler(
    request: fastapi.Request, exc: GitPipelineJobNotFoundError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "err_code": "PIPELINE_JOB_NOT_FOUND",
                "reason": (
                    f"There was no job with the name '{exc.job_name}' in the last 20 runs of the pipeline",
                    "Please contact your administrator.",
                ),
            },
        ),
    )


async def git_pipeline_job_failed_handler(
    request: fastapi.Request, exc: GitPipelineJobFailedError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail={
                "err_code": "FAILED_JOB_FOUND",
                "reason": (
                    f"The last job with the name '{exc.job_name}' has failed.",
                    "Please contact your administrator.",
                ),
            },
        ),
    )


async def unknown_state_handler(
    request: fastapi.Request, exc: GitPipelineJobUnknownStateError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "err_code": "UNKNOWN_STATE_ERROR",
                "reason": (
                    f"Job '{exc.job_name}' has an unhandled or unknown state: '{exc.state}'",
                    "Please contact your administrator.",
                ),
            },
        ),
    )


async def github_artifact_expired_handler(
    request: fastapi.Request, _: GithubArtifactExpiredError
) -> fastapi.Response:
    return await exception_handlers.http_exception_handler(
        request,
        fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "err_code": "ARTIFACT_EXPIRED",
                "reason": (
                    "The last artifact you requested has expired.",
                    "Please rerun your pipeline or contact your administrator.",
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
    app.add_exception_handler(
        GitPipelineJobNotFoundError,
        git_pipeline_job_not_found_handler,
    )
    app.add_exception_handler(
        GitPipelineJobUnknownStateError, unknown_state_handler
    )
    app.add_exception_handler(
        GitPipelineJobFailedError,
        git_pipeline_job_failed_handler,
    )
