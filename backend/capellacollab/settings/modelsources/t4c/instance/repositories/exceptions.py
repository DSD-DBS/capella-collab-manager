# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class T4CRepositoryNotFoundError(core_exceptions.BaseError):
    def __init__(self, repository_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="T4C Repository not found",
            reason=f"T4C Repository with ID {repository_id} not found in our database.",
            err_code="T4C_REPOSITORY_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "T4CRepositoryNotFoundError":
        return cls(-1)


class T4CRepositoryDoesntBelongToServerError(core_exceptions.BaseError):
    def __init__(self, repository_id: int, server_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="T4C Repository doesn't belong to requested server",
            reason=f"T4C Repository with ID {repository_id} doesn't belong to server with ID {server_id}",
            err_code="T4C_REPOSITORY_DOESNT_BELONG_TO_SERVER",
        )

    @classmethod
    def openapi_example(cls) -> "T4CRepositoryDoesntBelongToServerError":
        return cls(-1, -1)


class T4CRepositoryAlreadyExistsError(core_exceptions.BaseError):
    def __init__(self, repository_name: str, instance_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="T4C Repository already exists",
            reason=f"T4C Repository with name '{repository_name}' already exists for the T4C server '{instance_name}' in our database.",
            err_code="T4C_REPOSITORY_ALREADY_EXISTS",
        )

    @classmethod
    def openapi_example(cls) -> "T4CRepositoryAlreadyExistsError":
        return cls("coffee-machine", "PROD")
