# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import models as users_models


class RequiredRoleNotMetError(core_exceptions.BaseError):
    def __init__(self, required_role: users_models.Role):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Minimum role not met",
            reason=f"The role {required_role.value} is required for this transaction.",
            err_code="REQUIRED_ROLE_NOT_MET",
        )


class RequiredProjectRoleNotMetError(core_exceptions.BaseError):
    def __init__(
        self,
        required_role: projects_users_models.ProjectUserRole,
        project_slug: str,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Minimum project role not met",
            reason=f"The role {required_role.value} in the project '{project_slug}' is required for this transaction.",
            err_code="REQUIRED_PROJECT_ROLE_NOT_MET",
        )


class RequiredProjectPermissionNotMetError(core_exceptions.BaseError):
    def __init__(
        self,
        required_permission: projects_users_models.ProjectUserPermission,
        project_slug: str,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Minimum project permission not met",
            reason=f"The permission {required_permission.value} in the project '{project_slug}' is required for this transaction.",
            err_code="REQUIRED_PROJECT_PERMISSION_NOT_MET",
        )


class UnknownScheme(core_exceptions.BaseError):
    def __init__(self, scheme: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Invalid scheme detected",
            reason=(
                f"The scheme '{scheme}' is not supported. "
                "Authentication is only supported via cookies or basic authentication."
            ),
            err_code="UNKNOWN_SCHEME",
        )


class TokenSignatureExpired(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Token signature expired",
            reason="The Signature of the token is expired. Please refresh the token or request a new access token.",
            err_code="TOKEN_SIGNATURE_EXPIRED",
        )


class RefreshTokenSignatureExpired(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Refresh token signature expired",
            reason="The Signature of the refresh token is expired. Please request a new access token.",
            err_code="REFRESH_TOKEN_EXPIRED",
        )


class JWTValidationFailed(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Token validation failed",
            reason="The validation of the access token failed. Please contact your administrator.",
            err_code="JWT_TOKEN_VALIDATION_FAILED",
        )


class JWTInvalidToken(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Access token not valid",
            reason="The used token is not valid.",
            err_code="JWT_TOKEN_INVALID",
        )


class UnauthenticatedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Unauthenticated",
            reason="Not authenticated",
            err_code="UNAUTHENTICATED",
        )


class InvalidPersonalAccessTokenError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Personal access token not valid.",
            reason="The used token is not valid.",
            err_code="BASIC_TOKEN_INVALID",
        )


class NonceMismatchError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="The nonce values do not match.",
            reason="The nonce value provided in the identity token does not match the generated nonce value.",
            err_code="NONCE_VALUE_MISMATCH",
        )


class RefreshTokenCookieMissingError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="No refresh token provided.",
            reason="There was no refresh token cookie provided",
            err_code="NO_REFRESH_TOKEN_COOKIE",
        )


class PersonalAccessTokenExpired(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="PAT expired",
            reason=(
                "The personal access token is expired."
                "Please request a new access token."
            ),
            err_code="PAT_EXPIRED",
        )
