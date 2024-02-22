# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from pydantic import BaseModel, Field

T = t.TypeVar("T")


class Message(BaseModel):
    err_code: str | None = Field(
        default=None,
        description="The HTTP response status code",
        examples=[
            "422 Unprocessable Content",
        ],
    )
    title: str | None = Field(
        default=None,
        description="The error title",
        examples=["Repository deletion failed partially."],
    )
    reason: str | tuple | None = Field(
        default=None,
        description="The user friendly error description",
        examples=["The TeamForCapella server is not reachable."],
    )
    technical: str | None = Field(
        default=None,
        description="The technical developer error description",
        examples=["TeamForCapella returned status code {e.status_code}"],
    )


class ResponseModel(BaseModel):
    warnings: list[Message] | None = Field(
        default=None,
        description="The list of warning message objects",
        examples=[
            [
                {
                    "err_code": "422 Unprocessable Content",
                    "title": "Repository deletion failed partially.",
                    "reason": "The TeamForCapella server is not reachable.",
                    "technical": "TeamForCapella returned status code {e.status_code}",
                }
            ]
        ],
    )
    errors: list[Message] | None = Field(
        default=None,
        description="The list of error message objects",
        examples=[
            [
                {
                    "err_code": "422 Unprocessable Content",
                    "title": "Repository deletion failed partially.",
                    "reason": "TeamForCapella returned an error when deleting the repository.",
                    "technical": "TeamForCapella returned status code {e.status_code}",
                }
            ]
        ],
    )


class PayloadResponseModel(ResponseModel, t.Generic[T]):
    payload: T
