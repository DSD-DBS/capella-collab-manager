# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import status

from capellacollab.core import exceptions as core_exceptions


class TagFoundError(core_exceptions.BaseError):
    def __init__(self, tag_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Tag not found",
            reason=f"The tag with the id '{tag_id}' was not found.",
            err_code="TAG_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "TagFoundError":
        return cls(-1)


class TagNameFoundError(core_exceptions.BaseError):
    def __init__(self, tag_name: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            title="Tag not found",
            reason=f"The tag with the name '{tag_name}' was not found.",
            err_code="TAG_NOT_FOUND",
        )

    @classmethod
    def openapi_example(cls) -> "TagNameFoundError":
        return cls("test")


class TagAlreadyExistsError(core_exceptions.BaseError):
    def __init__(self, tag_name: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            title="Tag already exists",
            reason=f"The tag with the name '{tag_name}' already exists.",
            err_code="TAG_ALREADY_EXISTS",
        )

    @classmethod
    def openapi_example(cls) -> "TagAlreadyExistsError":
        return cls("test")
