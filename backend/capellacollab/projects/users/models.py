# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base


class ProjectUserRole(enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "administrator"


class ProjectUserPermission(enum.Enum):
    READ = "read"
    WRITE = "write"


class ProjectUser(BaseModel):
    username: str
    role: ProjectUserRole
    permission: ProjectUserPermission

    class Config:
        orm_mode = True


class PatchProjectUser(BaseModel):
    role: t.Optional[ProjectUserRole]
    password: t.Optional[str]
    permission: t.Optional[ProjectUserPermission]


class ProjectUserAssociation(Base):
    __tablename__ = "project_user_association"

    username = Column(ForeignKey("users.name"), primary_key=True)
    projects_name = Column(ForeignKey("projects.name"), primary_key=True)
    user = relationship("DatabaseUser", back_populates="projects")
    projects = relationship("DatabaseProject", back_populates="users")
    permission = Column(Enum(ProjectUserPermission), nullable=False)
    role = Column(Enum(ProjectUserRole))
