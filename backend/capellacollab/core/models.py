# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = t.TypeVar("T")


class Message(BaseModel):
    err_code: str | None = None
    title: str | None = None
    reason: str | tuple | None = None
    technical: str | None = None


class ResponseModel(BaseModel):
    warnings: list[Message] | None = None
    errors: list[Message] | None = None


class PayloadResponseModel(ResponseModel, GenericModel, t.Generic[T]):
    payload: T
