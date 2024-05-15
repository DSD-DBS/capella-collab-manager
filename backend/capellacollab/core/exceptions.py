# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pydantic
from fastapi import status


@pydantic.dataclasses.dataclass
class BaseError(fastapi.HTTPException):
    status_code: int = pydantic.Field(
        description="The HTTP status code of an exception, accepts any int but passed as fastapi.status.DESIRED_STATUS_CODE for code readability",
        examples=[status.HTTP_404_NOT_FOUND],
    )
    title: str = pydantic.Field(
        description="The title of the error, displayed in the frontend",
        examples=["User not found"],
    )
    reason: str = pydantic.Field(
        description="The reason for the error and any possible resolutions/next steps, displayed in the frontend",
        examples=["The user 'username' doesn't exist."],
    )
    err_code: str = pydantic.Field(
        description="The error code of the error, used for logging and debugging, not displayed in the frontend.",
        examples=["USER_NOT_FOUND"],
    )
    headers: dict[str, str] = pydantic.Field(default_factory=dict)

    def __post_init__(self):
        super().__init__(
            status_code=self.status_code,
            detail={
                "title": self.title,
                "reason": self.reason,
                "err_code": self.err_code,
            },
            headers=self.headers,
        )


class ExistingDependenciesError(BaseError):
    def __init__(
        self, entity_name: str, entity_type: str, dependencies: list[str]
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title=f"{entity_name} cannot be deleted",
            reason=(
                f"The {entity_type} '{entity_name}' can not be deleted. "
                f"Please remove the following dependencies first: {', '.join(dependencies)}"
            ),
            err_code="EXISTING_DEPENDENCIES_PREVENT_DELETE",
        )


class ResourceAlreadyExistsError(BaseError):
    def __init__(
        self,
        resource_name: str | None = None,
        identifier_name: str | None = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title=f"{identifier_name} already used",
            reason=f"A {resource_name} with a similar {identifier_name} already exists.",
            err_code="RESOURCE_NAME_ALREADY_IN_USE",
        )
