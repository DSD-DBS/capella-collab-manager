# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    from capellacollab.projects.users.models import ProjectUserAssociation
    from capellacollab.sessions.models import DatabaseSession


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

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, index=True)
    role: Role = Column(Enum(Role))

    created = Column(DateTime)
    last_login = Column(DateTime)

    projects: list[ProjectUserAssociation] = relationship(
        "ProjectUserAssociation",
        back_populates="user",
    )
    sessions: DatabaseSession = relationship(
        "DatabaseSession",
        back_populates="owner",
    )
    events = relationship(
        "DatabaseUserHistoryEvent",
        back_populates="user",
        foreign_keys="DatabaseUserHistoryEvent.user_id",
    )
