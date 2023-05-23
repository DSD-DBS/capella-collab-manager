# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime
import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    from capellacollab.projects.users.models import ProjectUserAssociation
    from capellacollab.sessions.models import DatabaseSession
    from capellacollab.users.events.models import DatabaseUserHistoryEvent


class Role(enum.Enum):
    USER = "user"
    ADMIN = "administrator"


class BaseUser(BaseModel):
    name: str
    role: Role

    class Config:
        orm_mode = True


class User(BaseUser):
    id: str


class PatchUserRoleRequest(BaseModel):
    role: Role
    reason: str


class PostUser(BaseModel):
    name: str
    role: Role
    reason: str


class DatabaseUser(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(unique=True, index=True)
    role: Mapped[Role]
    created: Mapped[datetime.datetime | None]
    last_login: Mapped[datetime.datetime | None]

    projects: Mapped[list[ProjectUserAssociation]] = relationship(
        back_populates="user"
    )
    sessions: Mapped[list[DatabaseSession]] = relationship(
        back_populates="owner"
    )
    events: Mapped[list[DatabaseUserHistoryEvent]] = relationship(
        back_populates="user", foreign_keys="DatabaseUserHistoryEvent.user_id"
    )
