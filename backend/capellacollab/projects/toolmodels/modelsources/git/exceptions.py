# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class GitRepositoryNotFoundError(core_exceptions.BaseError):
    def __init__(self, git_model_id: int, tool_model_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Git repository not found",
            reason=(
                f"No Git repository with the ID '{git_model_id}' found for the model with slug {tool_model_slug}."
            ),
            err_code="GIT_REPOSITORY_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "GitRepositoryNotFoundError":
        return cls(-1, "coffee-machine")


class NoGitRepositoryAssignedToModelError(core_exceptions.BaseError):
    def __init__(self, tool_model_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="No Git repository assigned to model",
            reason=(
                f"No Git repository is assigned to the model with slug '{tool_model_slug}'."
            ),
            err_code="NO_GIT_REPOSITORY_ASSIGNED_TO_MODEL",
        )

    @classmethod
    def openapi_example(cls) -> "NoGitRepositoryAssignedToModelError":
        return cls("coffee-machine")


class GitRepositoryUsedInPipelines(core_exceptions.BaseError):
    def __init__(self, git_model_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Git repository used in pipelines",
            reason=(
                f"Git repository with the ID '{git_model_id}' is currently used in pipelines. "
                "Please remove the pipeline first."
            ),
            err_code="GIT_REPOSITORY_USED_IN_PIPELINES",
        )

    @classmethod
    def openapi_example(cls) -> "GitRepositoryUsedInPipelines":
        return cls(-1)


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

    @classmethod
    def openapi_example(cls) -> "GitRepositoryFileNotFoundError":
        return cls("README.md")


class GitPipelineJobNotFoundError(core_exceptions.BaseError):
    def __init__(self, job_name: str, revision: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Job not found",
            reason=(
                f"There was no job with the name '{job_name}' in the last 20 runs of the pipelines with revision '{revision}'. "
                "Please contact your administrator."
            ),
            err_code="PIPELINE_JOB_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "GitPipelineJobNotFoundError":
        return cls("update_capella_diagram_cache", "main")


class GitPipelineJobUnsuccessfulError(core_exceptions.BaseError):
    def __init__(self, job_name: str, state: str):
        self.job_name = job_name
        self.state = state
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Unsuccessful job",
            reason=(
                f"Job '{job_name}' has an unsuccessful state: {self.state}."
                "Please contact your administrator."
            ),
            err_code="UNSUCCESSFUL_JOB_STATE_ERROR",
        )

    @classmethod
    def openapi_example(cls) -> "GitPipelineJobUnsuccessfulError":
        return cls("update_capella_diagram_cache", "failed")


class GitHubArtifactExpiredError(core_exceptions.BaseError):
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

    @classmethod
    def openapi_example(cls) -> "GitHubArtifactExpiredError":
        return cls()
