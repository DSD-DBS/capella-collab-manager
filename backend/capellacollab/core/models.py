# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from pydantic import BaseModel


class Message(BaseModel):
    err_code: t.Optional[str]
    title: t.Optional[str]
    reason: t.Optional[t.Union[str, tuple]]
    technical: t.Optional[str]


class ResponseModel(BaseModel):
    warnings: t.Optional[list["Message"]]
    errors: t.Optional[list["Message"]]
