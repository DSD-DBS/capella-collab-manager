# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from fastapi import status

from .. import exceptions as git_exceptions


class GitlabAccessDeniedError(git_exceptions.AccessDeniedError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Insufficient Gitlab API access scope",
            reason=(
                "The registered token has not enough permissions to access the Gitlab API. "
                "Access scope 'read_api' is required. Please contact your project lead."
            ),
            err_code="GITLAB_ACCESS_DENIED",
        )


class GitlabProjectNotFoundError(git_exceptions.RepositoryNotFoundError):
    def __init__(self, project_name: str):
        self.project_name = project_name
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Project not found",
            reason=(
                f"We couldn't find the project in your Gitlab instance. "
                f"Please make sure that a project with the encoded name '{project_name}' does exist."
            ),
            err_code="PROJECT_NOT_FOUND",
        )
