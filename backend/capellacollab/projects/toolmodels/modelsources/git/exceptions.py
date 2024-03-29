# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class AccessDeniedError(core_exceptions.BaseError, metaclass=abc.ABCMeta):
    pass


class RepositoryNotFoundError(
    core_exceptions.BaseError, metaclass=abc.ABCMeta
):
    pass


class GitRepositoryFileNotFoundError(core_exceptions.BaseError):
    filename: str

    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="File not found",
            reason=(
                f"No file with the name '{filename}' found in the linked Git repository. "
                "Please contact your administrator."
            ),
            err_code="FILE_NOT_FOUND",
        )


class GitInstanceAPIEndpointNotFoundError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Git instance API endpoint not found",
            reason=(
                "The used Git instance has no API endpoint defined. "
                "Please contact your administrator."
            ),
            err_code="GIT_INSTANCE_NO_API_ENDPOINT_DEFINED",
        )


class GitPipelineJobNotFoundError(core_exceptions.BaseError):
    job_name: str

    def __init__(self, job_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Job not found",
            reason=(
                f"There was no job with the name '{job_name}' in the last 20 runs of the pipeline. "
                "Please contact your administrator."
            ),
            err_code="PIPELINE_JOB_NOT_FOUND",
        )


class GitPipelineJobFailedError(core_exceptions.BaseError):
    def __init__(self, job_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Failed job found",
            reason=f"The last job with the name '{job_name}' has failed.",
            err_code="FAILED_JOB_FOUND",
        )


class GitPipelineJobUnknownStateError(core_exceptions.BaseError):
    job_name: str
    state: str

    def __init__(self, job_name: str, state: str):
        self.job_name = job_name
        self.state = state
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Unknown job state",
            reason=(
                f"Job '{job_name}' has an unhandled or unknown state: '{state}'. "
                "Please contact your administrator."
            ),
            err_code="UNKNOWN_STATE_ERROR",
        )


class GithubArtifactExpiredError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Artifact expired",
            reason=(
                "The last artifact you requested has expired. "
                "Please rerun your pipeline or contact your administrator."
            ),
            err_code="ARTIFACT_EXPIRED",
        )
