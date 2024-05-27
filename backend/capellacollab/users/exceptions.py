# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class UserNotFoundError(core_exceptions.BaseError):
    def __init__(
        self, username: str | None = None, user_id: int | None = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="User not found",
            reason=f"The user '{username or user_id}' doesn't exist.",
            err_code="USER_NOT_FOUND",
        )


class NoProjectsInCommonError(core_exceptions.BaseError):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="No projects in common",
            reason=(
                f"The user with id {user_id} doesn't have any projects in common with you."
            ),
            err_code="NO_PROJECTS_IN_COMMON",
        )
