# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class T4CInstanceIsArchivedError(core_exceptions.BaseError):
    def __init__(self, t4c_instance_id: int):
        self.t4c_instance_id = t4c_instance_id
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="T4C instance is archived",
            reason=f"The T4C instance identified by {t4c_instance_id} is archived, thus prohibiting the execution of the requested operation.",
            err_code="T4C_INSTANCE_IS_ARCHIVED",
        )


class T4CInstanceNotFoundError(core_exceptions.BaseError):
    def __init__(self, t4c_instance_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="T4C server instance not found",
            reason=f"The T4C instance with id {t4c_instance_id} was not found.",
            err_code="T4C_INSTANCE_NOT_FOUND",
        )


class T4CInstanceWithNameAlreadyExistsError(
    core_exceptions.ResourceAlreadyExistsError
):
    def __init__(self):
        super().__init__(resource_name="T4C Instance", identifier_name="name")


class LicenseServerTimeoutError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server timeout",
            reason="The connection to the license server timed out.",
            err_code="T4C_LICENSE_SERVER_TIMEOUT",
        )


class LicenseServerConnectionFailedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server connection failed",
            reason="The connection to the license server failed.",
            err_code="T4C_LICENSE_SERVER_CONNECTION_FAILED",
        )


class LicenseServerInternalError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server internal error",
            reason="The license server returned an internal error.",
            err_code="T4C_LICENSE_SERVER_INTERNAL_ERROR",
        )


class LicenseServerNoStatusError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server has no status",
            reason="No status is available. This can happen during and after license server restarts.",
            err_code="T4C_LICENSE_SERVER_NO_STATUS",
        )


class LicenseServerNoStatusInResponse(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server has no status in response",
            reason="No status in response from license server.",
            err_code="T4C_LICENSE_SERVER_NO_STATUS_IN_JSON",
        )


class LicenseServerResponseDecodeError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="License server decode error",
            reason="License server response couldn't be decoded.",
            err_code="T4C_LICENSE_SERVER_DECODE_ERROR",
        )


class LicenseServerUnknownError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            title="License server unknown error",
            reason="An unknown error occurred when communicating with the license server.",
            err_code="T4C_LICENSE_SERVER_UNKNOWN_ERROR",
        )
