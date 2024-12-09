# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import datetime
import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.core import models as core_models
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects import models as projects_models
from capellacollab.sessions import models2 as sessions_models2
from capellacollab.sessions import operators
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

from . import injection

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.projects.toolmodels.provisioning.models import (
        DatabaseModelProvisioning,
    )
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
    revision: str | None = None
    deep_clone: bool


class PostSessionRequest(core_pydantic.BaseModel):
    tool_id: int
    version_id: int

    session_type: SessionType = pydantic.Field(default=SessionType.PERSISTENT)
    connection_method_id: str | None = pydantic.Field(
        default=None,
        description=(
            "The identifier of the connection method to use."
            " If None, the default connection method will be used."
        ),
    )
    provisioning: list[SessionProvisioningRequest] = pydantic.Field(default=[])
    project_slug: str | None = pydantic.Field(
        default=None,
        description=(
            "The project to run the session in."
            " Required for persistent provisioned sessions."
            " Ignored for readonly sessions."
        ),
    )


class SessionSharing(core_pydantic.BaseModel):
    user: users_models.BaseUser
    created_at: datetime.datetime


class SessionPreparationState(enum.Enum):
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    PENDING = "Pending"
    NOT_FOUND = "NotFound"
    UNKNOWN = "Unknown"


class SessionState(enum.Enum):
    RUNNING = "Running"
    FAILED = "Failed"
    TERMINATED = "Terminated"
    PENDING = "Pending"
    NOT_FOUND = "NotFound"
    UNKNOWN = "Unknown"


class Session(core_pydantic.BaseModel):
    id: str
    type: SessionType
    created_at: datetime.datetime
    owner: users_models.BaseUser

    version: tools_models.ToolVersionWithTool

    preparation_state: SessionPreparationState = pydantic.Field(
        default=SessionPreparationState.UNKNOWN
    )
    state: SessionState = pydantic.Field(default=SessionState.UNKNOWN)
    warnings: list[core_models.Message] = pydantic.Field(default=[])
    idle_state: sessions_models2.IdleState = pydantic.Field(
        default=sessions_models2.IdleState(
            available=False,
            terminate_after_minutes=config.sessions.timeout,
            unavailable_reason="Uninitialized",
        )
    )

    connection_method_id: str
    connection_method: tools_models.ToolSessionConnectionMethod | None = None

    shared_with: list[SessionSharing] = pydantic.Field(default=[])

    project: projects_models.SimpleProject | None = pydantic.Field(
        default=None
    )

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
        self.idle_state = injection.get_idle_state(self.id)
        self.preparation_state, self.state = (
            operators.get_operator().get_session_state(self.id)
        )

        return self


class ShareSessionRequest(core_pydantic.BaseModel):
    username: str


class SessionConnectionInformation(core_pydantic.BaseModel):
    """Information about the connection to the session."""

    local_storage: dict[str, str] = pydantic.Field(
        description=(
            "Configuration for the local storage of the frontend. "
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

    provisioning_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("model_provisioning.id"),
        init=False,
    )
    provisioning: orm.Mapped[DatabaseModelProvisioning | None] = (
        orm.relationship(
            back_populates="session",
            foreign_keys=[provisioning_id],
            default=None,
        )
    )

    project_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("projects.id"),
        init=False,
    )
    project: orm.Mapped[DatabaseProject | None] = orm.relationship(
        foreign_keys=[project_id],
        default=None,
    )

    environment: orm.Mapped[dict[str, str]] = orm.mapped_column(
        nullable=False, default_factory=dict
    )
    config: orm.Mapped[dict[str, str]] = orm.mapped_column(
        nullable=False, default_factory=dict
    )

    shared_with: orm.Mapped[list[DatabaseSharedSession]] = orm.relationship(
        "DatabaseSharedSession",
        back_populates="session",
        init=False,
        cascade="all, delete-orphan",
    )


class DatabaseSharedSession(database.Base):
    __tablename__ = "shared_sessions"

    id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        init=False,
        primary_key=True,
        index=True,
        unique=True,
        autoincrement=True,
    )
    created_at: orm.Mapped[datetime.datetime]

    session_id: orm.Mapped[str] = orm.mapped_column(
        sa.ForeignKey("sessions.id"), primary_key=True, init=False
    )
    session: orm.Mapped[DatabaseSession] = orm.relationship(
        back_populates="shared_with"
    )

    user_id: orm.Mapped[str] = orm.mapped_column(
        sa.ForeignKey("users.id"), primary_key=True, init=False
    )
    user: orm.Mapped[DatabaseUser] = orm.relationship()
