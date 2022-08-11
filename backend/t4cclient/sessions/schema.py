# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
import datetime
import enum
import numbers
import typing as t

# 3rd party:
from pydantic import BaseModel

# local:
from t4cclient.sessions.operators.k8s import FileType
from t4cclient.schemas.repositories import RepositoryUserPermission


class WorkspaceType(enum.Enum):
    PERSISTENT = "persistent"
    READONLY = "readonly"


class DepthType(enum.Enum):
    LatestCommit = "LatestCommit"
    CompleteHistory = "CompleteHistory"


class GetSessionsResponse(BaseModel):
    id: str
    type: WorkspaceType
    ports: t.List[str]
    created_at: datetime.datetime
    owner: str
    repository: t.Optional[str]
    state: str
    guacamole_username: str
    guacamole_connection_id: str
    last_seen: str

    class Config:
        orm_mode = True


class AdvancedSessionResponse(GetSessionsResponse):
    rdp_password: str

    class Config:
        orm_mode = True


class FileTree(BaseModel):
    path: str
    name: str
    type: FileType
    children: t.Optional[list[FileTree]]

    class Config:
        orm_mode = True


class PostSessionRequest(BaseModel):
    type: WorkspaceType
    branch: str
    depth: DepthType
    repository: t.Optional[str]

    class Config:
        orm_mode = True


class GetSessionUsageResponse(BaseModel):
    free: int
    total: int
    errors: t.List[str]

    class Config:
        orm_mode = True


class GuacamoleAuthentication(BaseModel):
    token: str
    url: str

    class Config:
        orm_mode = True
