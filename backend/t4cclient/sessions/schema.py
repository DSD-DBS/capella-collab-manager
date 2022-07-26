# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum
import typing as t

from pydantic import BaseModel


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
