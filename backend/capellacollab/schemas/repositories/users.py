# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    USER = "user"
    ADMIN = "administrator"


class PatchUserRoleRequest(BaseModel):
    role: Role


class GetUserResponse(BaseModel):
    id: str
    name: str
    role: Role

    class Config:
        orm_mode = True
