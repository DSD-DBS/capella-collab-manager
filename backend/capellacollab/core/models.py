# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import pydantic

from capellacollab.core import pydantic as core_pydantic

T = t.TypeVar("T")


class Message(core_pydantic.BaseModel):
    err_code: str = pydantic.Field(
        description="The error code of the message, used for testing, not displayed in the frontend.",
        examples=["T4C_SERVER_UNREACHABLE"],
    )
    title: str = pydantic.Field(
        description="The title of the message, displayed in the frontend",
        examples=["TeamForCapella server not reachable"],
    )
    reason: str = pydantic.Field(
        description="The reason for the message and any possible resolutions/next steps, displayed in the frontend",
        examples=["We will only show a representation of our database."],
    )


class ResponseModel(core_pydantic.BaseModel):
    warnings: list[Message] | None = None
    errors: list[Message] | None = None


class PayloadResponseModel[T](ResponseModel):
    payload: T
