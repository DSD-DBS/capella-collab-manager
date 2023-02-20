# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime
import enum

from pydantic import BaseModel

from capellacollab.core.models import Message
from capellacollab.projects.models import Project
from capellacollab.sessions.operators.k8s import FileType
from capellacollab.tools.models import ToolVersionWithTool
from capellacollab.users.models import BaseUser


class WorkspaceType(enum.Enum):
    PERSISTENT = "persistent"
    READONLY = "readonly"


class DepthType(enum.Enum):
    LatestCommit = "LatestCommit"
    CompleteHistory = "CompleteHistory"


class GetSessionsResponse(BaseModel):
    id: str
    type: WorkspaceType
    created_at: datetime.datetime
    owner: BaseUser
    state: str
    guacamole_username: str | None
    guacamole_connection_id: str | None
    warnings: list[Message] | None
    last_seen: str
    project: Project | None
    version: ToolVersionWithTool | None

    class Config:
        orm_mode = True


class OwnSessionResponse(GetSessionsResponse):
    t4c_password: str | None
    jupyter_token: str | None
    session_domain: str | None


class PostReadonlySessionEntry(BaseModel):
    model_slug: str
    git_model_id: int
    revision: str
    deep_clone: bool


class PostReadonlySessionRequest(BaseModel):
    models: list[PostReadonlySessionEntry]

    class Config:
        orm_mode = True


class PostPersistentSessionRequest(BaseModel):
    tool_id: int
    version_id: int

    class Config:
        orm_mode = True


class GetSessionUsageResponse(BaseModel):
    free: int
    total: int

    class Config:
        orm_mode = True


class GuacamoleAuthentication(BaseModel):
    token: str
    url: str

    class Config:
        orm_mode = True


class FileTree(BaseModel):
    path: str
    name: str
    type: FileType
    children: list[FileTree] | None

    class Config:
        orm_mode = True
