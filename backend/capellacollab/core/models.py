# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from pydantic import BaseModel


class Message(BaseModel):
    err_code: str | None
    title: str | None
    reason: t.Union[str, tuple] | None
    technical: str | None


class ResponseModel(BaseModel):
    warnings: list["Message"] | None
    errors: list["Message"] | None
