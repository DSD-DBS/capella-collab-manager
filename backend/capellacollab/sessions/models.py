# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import datetime
import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import models as core_models
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects import models as projects_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

if t.TYPE_CHECKING:
    from capellacollab.tools.models import DatabaseTool, DatabaseVersion
    from capellacollab.users.models import DatabaseUser


class WorkspaceType(enum.Enum):
    PERSISTENT = "persistent"
    READONLY = "readonly"


class Session(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: str
    type: WorkspaceType
    created_at: datetime.datetime
    owner: users_models.BaseUser

    guacamole_username: str | None = None
    guacamole_connection_id: str | None = None

    project: projects_models.Project | None = None
    version: tools_models.ToolVersionWithTool | None = None

    _validate_created_at = pydantic.field_serializer("created_at")(
        core_pydantic.datetime_serializer
    )


class GetSessionsResponse(Session):
    state: str
    warnings: list[core_models.Message] | None = None
    last_seen: str

    t4c_password: str | None = None
    jupyter_uri: str | None = None


class PostReadonlySessionEntry(pydantic.BaseModel):
    toolmodel_slug: str = pydantic.Field(alias="model_slug")
    git_model_id: int
    revision: str
    deep_clone: bool


class PostReadonlySessionRequest(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    models: list[PostReadonlySessionEntry]


class PostPersistentSessionRequest(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    tool_id: int
    version_id: int


class GetSessionUsageResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    free: int
    total: int


class GuacamoleAuthentication(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    token: str
    url: str


class DatabaseSession(database.Base):
    __tablename__ = "sessions"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True, index=True)

    ports: orm.Mapped[list[int]] = orm.mapped_column(sa.ARRAY(sa.Integer))
    created_at: orm.Mapped[datetime.datetime]

    rdp_password: orm.Mapped[str | None]
    guacamole_username: orm.Mapped[str | None]
    guacamole_password: orm.Mapped[str | None]
    guacamole_connection_id: orm.Mapped[str | None]

    host: orm.Mapped[str]
    type: orm.Mapped[WorkspaceType]

    owner_name: orm.Mapped[str] = orm.mapped_column(
        sa.ForeignKey("users.name")
    )
    owner: orm.Mapped[DatabaseUser] = orm.relationship()

    tool_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("tools.id"))
    tool: orm.Mapped[DatabaseTool] = orm.relationship()

    version_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("versions.id")
    )
    version: orm.Mapped[DatabaseVersion] = orm.relationship()

    project_id: orm.Mapped[str | None] = orm.mapped_column(
        sa.ForeignKey("projects.id")
    )
    project: orm.Mapped[projects_models.DatabaseProject] = orm.relationship()

    environment: orm.Mapped[dict[str, str] | None]
