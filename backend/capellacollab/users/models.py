# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime
import enum
import typing as t

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

if t.TYPE_CHECKING:
    from capellacollab.events.models import DatabaseUserHistoryEvent
    from capellacollab.projects.users.models import ProjectUserAssociation
    from capellacollab.sessions.models import DatabaseSession
    from capellacollab.users.tokens.models import DatabaseUserToken


class Role(enum.Enum):
    USER = "user"
    ADMIN = "administrator"


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        description="The name of a user", examples=["John Doe"], max_length=50
    )
    role: Role = Field(
        description="The application-level role of a user", examples=["user"]
    )


class User(BaseUser):
    id: int
    created: datetime.datetime | None = Field(
        default=None,
        description="The time a user was created",
        examples=["2021-01-01T12:00:00Z"],
    )
    last_login: datetime.datetime | None = Field(
        default=None,
        description="The time a user last logged in",
        examples=["2021-01-01T12:00:00Z"],
    )

    _validate_created = field_serializer("created")(
        core_pydantic.datetime_serializer
    )
    _validate_last_login = field_serializer("last_login")(
        core_pydantic.datetime_serializer
    )


class PatchUserRoleRequest(BaseModel):
    role: Role = Field(
        description="The application-level role of a user provided for patching",
        examples=["admin"],
    )
    reason: str = Field(
        description="The rationale provided for patching a user's role",
        examples=["User transfered to support team"],
    )


class PostUser(BaseModel):
    name: str = Field(
        description="The name of a user provided at creation",
        examples=["superuser@hotmail.com"],
        max_length=50,
    )
    role: Role = Field(
        description="The application-level role of a user provided at creation",
        examples=["admin"],
    )
    reason: str = Field(
        description="The rationale provided for creating a user",
        examples=["New hire"],
        max_length=255,
    )


class DatabaseUser(database.Base):
    __tablename__ = "users"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, index=True)

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    role: orm.Mapped[Role]
    created: orm.Mapped[datetime.datetime | None]
    last_login: orm.Mapped[datetime.datetime | None]

    projects: orm.Mapped[list[ProjectUserAssociation]] = orm.relationship(
        back_populates="user"
    )
    sessions: orm.Mapped[list[DatabaseSession]] = orm.relationship(
        back_populates="owner"
    )
    events: orm.Mapped[list[DatabaseUserHistoryEvent]] = orm.relationship(
        back_populates="user", foreign_keys="DatabaseUserHistoryEvent.user_id"
    )

    tokens: orm.Mapped[list[DatabaseUserToken]] = orm.relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
