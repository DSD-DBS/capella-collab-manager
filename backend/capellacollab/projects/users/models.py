# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base
from capellacollab.users.models import DatabaseUser, User

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject


class ProjectUserRole(enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "administrator"


class ProjectUserPermission(enum.Enum):
    READ = "read"
    WRITE = "write"


class ProjectUser(BaseModel):
    role: ProjectUserRole
    permission: ProjectUserPermission
    user: User

    class Config:
        orm_mode = True


class PostProjectUser(BaseModel):
    role: ProjectUserRole
    permission: ProjectUserPermission
    username: str
    reason: str


class PatchProjectUser(BaseModel):
    role: ProjectUserRole | None
    permission: ProjectUserPermission | None
    reason: str


class ProjectUserAssociation(Base):
    __tablename__ = "project_user_association"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True
    )
    user: Mapped[DatabaseUser] = relationship(back_populates="projects")

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), primary_key=True
    )
    project: Mapped["DatabaseProject"] = relationship(back_populates="users")

    permission: Mapped[ProjectUserPermission]
    role: Mapped[ProjectUserRole]
