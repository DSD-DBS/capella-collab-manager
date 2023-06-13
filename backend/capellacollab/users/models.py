# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime
import enum
import typing as t

import pydantic
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.projects.users.models import ProjectUserAssociation
    from capellacollab.sessions.models import DatabaseSession
    from capellacollab.users.events.models import DatabaseUserHistoryEvent


class Role(enum.Enum):
    USER = "user"
    ADMIN = "administrator"


class BaseUser(pydantic.BaseModel):
    name: str
    role: Role

    class Config:
        orm_mode = True


class User(BaseUser):
    id: str


class PatchUserRoleRequest(pydantic.BaseModel):
    role: Role
    reason: str


class PostUser(pydantic.BaseModel):
    name: str
    role: Role
    reason: str


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
