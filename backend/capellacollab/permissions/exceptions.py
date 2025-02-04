# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions

from . import models


class InsufficientPermissionError(core_exceptions.BaseError):
    def __init__(
        self,
        required_permission: str,
        required_verbs: set[models.UserTokenVerb],
    ):
        verbs = ", ".join(verb.value for verb in required_verbs)
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            title="Permission denied",
            reason=f"Insufficient permissions: '{required_permission}' permission with verb(s) {verbs} is required for this transaction.",
            err_code="INSUFFICIENT_PERMISSION",
        )

    @classmethod
    def openapi_example(cls) -> "InsufficientPermissionError":
        return cls(
            "group.permission",
            {models.UserTokenVerb.GET, models.UserTokenVerb.CREATE},
        )


class InvalidPermissionFormatError(core_exceptions.BaseError):
    def __init__(self, permission: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Invalid permission format",
            reason=(
                f"The scope '{permission}' has an invalid format."
                " It has to be in the format 'group.permission:verb'."
            ),
            err_code="INVALID_PERMISSION_FORMAT",
        )

    @classmethod
    def openapi_example(cls) -> "InvalidPermissionFormatError":
        return cls("group.permission")


class PermissionOrVerbNotFoundError(core_exceptions.BaseError):
    def __init__(self, permission: str, verb: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            title="Invalid permission or verb",
            reason=(
                f"The permission '{permission}' with verb '{verb}' is not valid."
            ),
            err_code="PERMISSION_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "PermissionOrVerbNotFoundError":
        return cls("admin.user2", "get")
