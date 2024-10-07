# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class T4CLicenseServerTimeoutError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server timeout",
            reason="The connection to the license server timed out.",
            err_code="T4C_LICENSE_SERVER_TIMEOUT",
        )


class T4CLicenseServerConnectionFailedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server connection failed",
            reason="The connection to the license server failed.",
            err_code="T4C_LICENSE_SERVER_CONNECTION_FAILED",
        )


class T4CLicenseServerInternalError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server internal error",
            reason="The license server returned an internal error.",
            err_code="T4C_LICENSE_SERVER_INTERNAL_ERROR",
        )


class T4CLicenseServerNoStatusError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server has no status",
            reason=(
                "No status is available. This can happen during and after license server restarts. "
                "The license information will be available when a client claims a license."
            ),
            err_code="T4C_LICENSE_SERVER_NO_STATUS",
        )


class T4CLicenseServerNoStatusInResponse(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server has no status in response",
            reason="No status in response from license server.",
            err_code="T4C_LICENSE_SERVER_NO_STATUS_IN_JSON",
        )


class T4CLicenseServerResponseDecodeError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server decode error",
            reason="License server response couldn't be decoded.",
            err_code="T4C_LICENSE_SERVER_DECODE_ERROR",
        )


class T4CLicenseServerUnknownError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            title="License server unknown error",
            reason="An unknown error occurred when communicating with the license server.",
            err_code="T4C_LICENSE_SERVER_UNKNOWN_ERROR",
        )


class T4CLicenseServerWithNameAlreadyExistsError(
    core_exceptions.ResourceAlreadyExistsError
):
    def __init__(self):
        super().__init__(
            resource_name="T4C License Server", identifier_name="name"
        )


class T4CLicenseServerNotFoundError(core_exceptions.BaseError):
    def __init__(self, t4c_license_server_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="T4C license server not found",
            reason=f"The T4C license server with id {t4c_license_server_id} was not found.",
            err_code="T4C_LICENSE_SERVER_NOT_FOUND",
        )


class T4CLicenseServerInUseError(core_exceptions.BaseError):
    def __init__(self, t4c_license_server_id: int):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="T4C license server in use",
            reason=f"The T4C license server with id {t4c_license_server_id} is in use.",
            err_code="T4C_LICENSE_SERVER_IN_USE",
        )
