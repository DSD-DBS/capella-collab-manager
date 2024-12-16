# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class SessionFileLoadingFailedError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Loading files failed",
            reason="Loading the files of the session failed.",
            err_code="FILES_LOADING_FAILED",
        )

    @classmethod
    def openapi_example(cls) -> "SessionFileLoadingFailedError":
        return cls()


class FileSizeExceededError(core_exceptions.BaseError):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            title="File size exceeded",
            reason="The summed file size must not exceed 30MB.",
            err_code="FILE_SIZE_EXCEEDED",
        )

    @classmethod
    def openapi_example(cls) -> "FileSizeExceededError":
        return cls()
