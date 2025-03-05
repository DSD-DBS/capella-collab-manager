# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class TokenNotFoundError(core_exceptions.BaseError):
    def __init__(self, token_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            err_code="TOKEN_NOT_FOUND",
            title="Token not found",
            reason=f"The token with id {token_id} was not found.",
        )

    @classmethod
    def openapi_example(cls) -> "TokenNotFoundError":
        return cls(-1)


class ManagedTokensRestrictionError(core_exceptions.BaseError):
    def __init__(self, token_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            err_code="MANAGED_TOKEN_RESTRICTED",
            title=f"Managed token {token_id} is restricted",
            reason="Managed tokens are restricted and can't be removed.",
        )

    @classmethod
    def openapi_example(cls) -> "ManagedTokensRestrictionError":
        return cls(-1)
