# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


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

    @classmethod
    def openapi_example(cls) -> "UnknownScheme":
        return cls("bearer")


class TokenSignatureExpired(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Token signature expired",
            reason="The Signature of the token is expired. Please refresh the token or request a new access token.",
            err_code="TOKEN_SIGNATURE_EXPIRED",
        )

    @classmethod
    def openapi_example(cls) -> "TokenSignatureExpired":
        return cls()


class RefreshTokenSignatureExpired(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Refresh token signature expired",
            reason="The Signature of the refresh token is expired. Please request a new access token.",
            err_code="REFRESH_TOKEN_EXPIRED",
        )

    @classmethod
    def openapi_example(cls) -> "RefreshTokenSignatureExpired":
        return cls()


class JWTValidationFailed(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Token validation failed",
            reason="The validation of the access token failed. Please contact your administrator.",
            err_code="JWT_TOKEN_VALIDATION_FAILED",
        )

    @classmethod
    def openapi_example(cls) -> "JWTValidationFailed":
        return cls()


class JWTInvalidToken(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Access token not valid",
            reason="The used token is not valid.",
            err_code="JWT_TOKEN_INVALID",
        )

    @classmethod
    def openapi_example(cls) -> "JWTInvalidToken":
        return cls()


class UnauthenticatedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Unauthenticated",
            reason="Not authenticated",
            err_code="UNAUTHENTICATED",
        )

    @classmethod
    def openapi_example(cls) -> "UnauthenticatedError":
        return cls()


class InvalidPersonalAccessTokenError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="Personal access token not valid.",
            reason="The used token is not valid.",
            err_code="BASIC_TOKEN_INVALID",
        )

    @classmethod
    def openapi_example(cls) -> "InvalidPersonalAccessTokenError":
        return cls()


class NonceMismatchError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="The nonce values do not match.",
            reason="The nonce value provided in the identity token does not match the generated nonce value.",
            err_code="NONCE_VALUE_MISMATCH",
        )

    @classmethod
    def openapi_example(cls) -> "NonceMismatchError":
        return cls()


class RefreshTokenCookieMissingError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="No refresh token provided.",
            reason="There was no refresh token cookie provided",
            err_code="NO_REFRESH_TOKEN_COOKIE",
        )

    @classmethod
    def openapi_example(cls) -> "RefreshTokenCookieMissingError":
        return cls()


class PersonalAccessTokenExpired(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            title="PAT expired",
            reason=(
                "The personal access token is expired."
                " Please request a new access token."
            ),
            err_code="PAT_EXPIRED",
        )

    @classmethod
    def openapi_example(cls) -> "PersonalAccessTokenExpired":
        return cls()
