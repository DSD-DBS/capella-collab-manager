# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class AdminNotAllowedAsProjectUserError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            err_code="ADMIN_NOT_ALLOWED_AS_PROJECT_USER",
            title="Administrators can't be added as project users",
            reason=(
                "Administrators already have full access to all projects. "
                "Therefore, they can't be added as project users."
            ),
        )


class ProjectUserAlreadyExistsError(core_exceptions.BaseError):
    def __init__(self, username: str, project_slug: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            err_code="PROJECT_USER_ALREADY_EXISTS",
            title="User already exists in project",
            reason=f"The user '{username}' already exists in the project '{project_slug}'.",
        )


class ProjectUserNotFoundError(core_exceptions.BaseError):
    def __init__(self, username: str, project_slug: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            err_code="PROJECT_USER_NOT_FOUND",
            title="User not found in project",
            reason=f"The user '{username}' was not found in the project '{project_slug}'.",
        )


class PermissionForProjectLeadsNotAllowedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            err_code="PERMISSION_FOR_PROJECT_LEADS_NOT_ALLOWED",
            title="Permission for project leads not allowed",
            reason=(
                "Project leads can't be given permissions. "
                "They already have full access to the project."
            ),
        )
