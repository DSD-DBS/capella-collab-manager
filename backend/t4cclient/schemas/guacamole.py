# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel


class GuacamoleAuthentication(BaseModel):
    token: str
    url: str

    class Config:
        orm_mode = True
