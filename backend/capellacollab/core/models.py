# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel


class Message(BaseModel):
    err_code: str | None
    title: str | None
    reason: str | tuple | None
    technical: str | None


class ResponseModel(BaseModel):
    warnings: list["Message"] | None
    errors: list["Message"] | None
