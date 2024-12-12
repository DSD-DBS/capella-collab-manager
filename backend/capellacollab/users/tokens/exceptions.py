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
