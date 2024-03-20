# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime
import enum
import typing as t

import pydantic
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


class BaseUser(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    role: Role


class User(BaseUser):
    id: int
    created: datetime.datetime | None = None
    last_login: datetime.datetime | None = None

    _validate_created = pydantic.field_serializer("created")(
        core_pydantic.datetime_serializer
    )
    _validate_last_login = pydantic.field_serializer("last_login")(
        core_pydantic.datetime_serializer
    )


class PatchUserRoleRequest(pydantic.BaseModel):
    role: Role
    reason: str


class PostUser(pydantic.BaseModel):
    name: str
    role: Role
    reason: str


class DatabaseUser(database.Base):
    __tablename__ = "users"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    role: orm.Mapped[Role]
    created: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        default=datetime.datetime.now(datetime.UTC)
    )

    projects: orm.Mapped[list[ProjectUserAssociation]] = orm.relationship(
        default_factory=list, back_populates="user"
    )
    sessions: orm.Mapped[list[DatabaseSession]] = orm.relationship(
        default_factory=list, back_populates="owner"
    )
    events: orm.Mapped[list[DatabaseUserHistoryEvent]] = orm.relationship(
        default_factory=list,
        back_populates="user",
        foreign_keys="DatabaseUserHistoryEvent.user_id",
    )

    tokens: orm.Mapped[list[DatabaseUserToken]] = orm.relationship(
        default_factory=list,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    last_login: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        default=None
    )
