# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel


class RepositoryUserRole(enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "administrator"


class RepositoryUserPermission(enum.Enum):
    READ = "read"
    WRITE = "write"


class Warning(enum.Enum):
    LICENCE_LIMIT = "LICENCE_LIMIT"
    NO_GIT_MODEL_DEFINED = "NO_GIT_MODEL_DEFINED"


class GetRepositoryUserResponse(BaseModel):
    repository_name: str
    role: RepositoryUserRole
    staged_by: str | None
    permissions: t.List[RepositoryUserPermission]
    warnings: t.List[Warning]

    class Config:
        orm_mode = True


class PostRepositoryRequest(BaseModel):
    name: str


class PostRepositoryUser(BaseModel):
    username: str
    role: RepositoryUserRole
    permission: RepositoryUserPermission

    class Config:
        orm_mode = True


class RepositoryUser(PostRepositoryUser):
    repository_name: str


class PatchRepositoryUser(BaseModel):
    role: t.Optional[RepositoryUserRole]
    password: t.Optional[str]
    permission: t.Optional[RepositoryUserPermission]


class StageRepositoryRequest(BaseModel):
    username: str
