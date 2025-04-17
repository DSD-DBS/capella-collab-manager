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

    @classmethod
    def openapi_example(cls) -> "UserNotFoundError":
        return cls("johndoe")


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

    @classmethod
    def openapi_example(cls) -> "NoProjectsInCommonError":
        return cls(-1)


class ReasonRequiredError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="No reason provided.",
            reason="You must provide a reason for this request.",
            err_code="REASON_REQUIRED",
        )

    @classmethod
    def openapi_example(cls) -> "ReasonRequiredError":
        return cls()


class ChangesNotAllowedForOtherUsersError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="You cannot make changes for other users",
            reason="Your role does not allow you to make changes for other users.",
            err_code="CHANGES_NOT_ALLOWED_FOR_OTHER_USERS",
        )

    @classmethod
    def openapi_example(cls) -> "ChangesNotAllowedForOtherUsersError":
        return cls()


class ChangesNotAllowedForRoleError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Changes not allowed for role",
            reason="Your role does not allow you to make these changes.",
            err_code="CHANGES_NOT_ALLOWED_FOR_ROLE",
        )

    @classmethod
    def openapi_example(cls) -> "ChangesNotAllowedForRoleError":
        return cls()


class BetaTestingDisabledError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Beta testing disabled",
            reason="Beta testing is currently disabled.",
            err_code="BETA_TESTING_DISABLED",
        )

    @classmethod
    def openapi_example(cls) -> "BetaTestingDisabledError":
        return cls()


class BetaTestingSelfEnrollmentNotAllowedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Beta testing self enrollment not allowed",
            reason="You do not have permission to enroll yourself in beta testing.",
            err_code="BETA_TESTING_SELF_ENROLLMENT_NOT_ALLOWED",
        )

    @classmethod
    def openapi_example(cls) -> "BetaTestingSelfEnrollmentNotAllowedError":
        return cls()


class UserBlockedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="The user is blocked.",
            reason=(
                "The user is blocked and all authenticated requests are rejected."
                " Contact your system administrator or support for help."
            ),
            err_code="USER_BLOCKED",
        )

    @classmethod
    def openapi_example(cls) -> "UserBlockedError":
        return cls()
