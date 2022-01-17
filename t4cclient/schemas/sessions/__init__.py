import datetime
import enum
import typing as t

from pydantic import BaseModel
from t4cclient.schemas.repositories import RepositoryUserPermission


class WorkspaceType(enum.Enum):
    PERSISTENT = "persistent"
    READONLY = "readonly"


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
    mac: str

    class Config:
        orm_mode = True


class AdvancedSessionResponse(GetSessionsResponse):
    rdp_password: str

    class Config:
        orm_mode = True


class PostSessionRequest(BaseModel):
    type: WorkspaceType
    repository: t.Optional[str]

    class Config:
        orm_mode = True


class GetSessionUsageResponse(BaseModel):
    free: int
    total: int

    class Config:
        orm_mode = True
