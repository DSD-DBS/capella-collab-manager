# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class GitRepositoryAccessError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Error while accessing the Git repository",
            reason=(
                "There was an error accessing the model. "
                "Please ask your project administrator for more information. "
                "In most cases, the credentials need to be updated."
            ),
            err_code="GIT_REPOSITORY_ACCESS_ERROR",
        )


class GitServerNotFound(core_exceptions.BaseError):
    def __init__(self, git_server_instance_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Git server not found",
            reason=f"The Git server with id {git_server_instance_id} was not found.",
            err_code="GIT_SERVER_NOT_FOUND",
        )


class InstancePrefixUnmatchedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="No Git instance with matching prefix found",
            reason=(
                "We couldn't find a matching Git instance. "
                "Make sure that your system administrator allows the given URL."
            ),
            err_code="NO_GIT_INSTANCE_WITH_PREFIX_FOUND",
        )


class RevisionNotFoundError(core_exceptions.BaseError):
    def __init__(self, revision: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Revision not found in repository",
            reason=f"The revision '{revision}' is not a valid branch or tag name.",
            err_code="GIT_REVISION_NOT_FOUND",
        )
