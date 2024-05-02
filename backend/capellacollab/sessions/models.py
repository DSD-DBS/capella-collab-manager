# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from . import injection

if t.TYPE_CHECKING:
    from capellacollab.tools.models import DatabaseTool, DatabaseVersion
    from capellacollab.users.models import DatabaseUser


class SessionType(enum.Enum):
    PERSISTENT = "persistent"
    READONLY = "readonly"


class SessionEnvironment(t.TypedDict):
    CAPELLACOLLAB_SESSION_TOKEN: str
    CAPELLACOLLAB_SESSION_ID: str
    CAPELLACOLLAB_SESSION_REQUESTER_USERNAME: str
    CAPELLACOLLAB_SESSION_CONNECTION_METHOD_TYPE: str
    CAPELLACOLLAB_SESSION_CONTAINER_PORT: str

    CAPELLACOLLAB_SESSIONS_SCHEME: t.Literal["http", "https"]
    CAPELLACOLLAB_SESSIONS_HOST: str
    CAPELLACOLLAB_SESSIONS_PORT: str
    CAPELLACOLLAB_SESSIONS_BASE_PATH: str

    CAPELLACOLLAB_ORIGIN_BASE_URL: str


class SessionProvisioningRequest(core_pydantic.BaseModel):
    project_slug: str
    toolmodel_slug: str = pydantic.Field(alias="model_slug")
    git_model_id: int
    revision: str
    deep_clone: bool


class PostSessionRequest(core_pydantic.BaseModel):
    tool_id: int
    version_id: int

    session_type: SessionType = pydantic.Field(default=SessionType.PERSISTENT)
    connection_method_id: str = pydantic.Field(
        description="The identifier of the connection method to use"
    )
    provisioning: list[SessionProvisioningRequest] = pydantic.Field(default=[])


class Session(core_pydantic.BaseModel):
    id: str
    type: SessionType
    created_at: datetime.datetime
    owner: users_models.BaseUser

    version: tools_models.ToolVersionWithTool

    state: str = pydantic.Field(default="UNKNOWN")
    warnings: list[core_models.Message] = pydantic.Field(default=[])
    last_seen: str = pydantic.Field(default="UNKNOWN")

    connection_method_id: str
    connection_method: tools_models.ToolSessionConnectionMethod | None = None

    _validate_created_at = pydantic.field_serializer("created_at")(
        core_pydantic.datetime_serializer
    )

    @pydantic.model_validator(mode="after")
    def resolve_connection_method(self) -> t.Any:
        self.connection_method = next(
            (
                method
                for method in self.version.tool.config.connection.methods
                if method.id == self.connection_method_id
            ),
            None,
        )
        return self

    @pydantic.model_validator(mode="after")
    def add_warnings_and_last_seen(self) -> t.Any:
        self.last_seen = injection.get_last_seen(self.id)
        self.state = injection.determine_session_state(self.id)

        return self


class SessionConnectionInformation(core_pydantic.BaseModel):
    """Information about the connection to the session."""

    local_storage: dict[str, str] = pydantic.Field(
        description=(
            "Configuration for the local storage of the frontend. "
            "The provided key/value pairs should be set by the frontend."
        ),
        default={},
    )

    cookies: dict[str, str] = pydantic.Field(
        description=(
            "Cookies, which are required to connect to the session. "
            "The provided key/value pairs should be set by the frontend."
        ),
        default={},
    )

    t4c_token: str | None = pydantic.Field(
        default=None, description="TeamForCapella session token"
    )
    redirect_url: str | None = pydantic.Field(
        default=None, description="URL for the client to redirect to"
    )


class DatabaseSession(database.Base):
    __tablename__ = "sessions"

    id: orm.Mapped[str] = orm.mapped_column(primary_key=True, index=True)

    created_at: orm.Mapped[datetime.datetime]
    type: orm.Mapped[SessionType]

    owner_name: orm.Mapped[str] = orm.mapped_column(
        sa.ForeignKey("users.name"), init=False
    )
    owner: orm.Mapped[DatabaseUser] = orm.relationship()

    tool_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("tools.id"), init=False
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship()

    version_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("versions.id"), init=False
    )
    version: orm.Mapped[DatabaseVersion] = orm.relationship()

    connection_method_id: orm.Mapped[str]

    environment: orm.Mapped[dict[str, str]] = orm.mapped_column(
        nullable=False, default_factory=dict
    )
    config: orm.Mapped[dict[str, str]] = orm.mapped_column(
        nullable=False, default_factory=dict
    )
