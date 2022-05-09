# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum
import typing as t

from pydantic import BaseModel


class Role(enum.Enum):
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


class RepositoryUserRole(enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "administrator"


class RepositoryUserPermission(enum.Enum):
    READ = "read"
    WRITE = "write"


class PostRepositoryUser(BaseModel):
    username: str
    role: RepositoryUserRole
    permission: RepositoryUserPermission

    class Config:
        orm_mode = True


class RepositoryUser(PostRepositoryUser):
    name: str


class PatchRepositoryUser(BaseModel):
    role: t.Optional[RepositoryUserRole]
    password: t.Optional[str]
    permission: t.Optional[RepositoryUserPermission]
