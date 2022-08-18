# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import enum
import typing as t

# 1st party:
from capellacollab.core.database import Base

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship


class Role(enum.Enum):
    USER = "user"
    ADMIN = "administrator"


class PatchUserRoleRequest(BaseModel):
    role: Role


class GetUserResponse(BaseModel):
    id: str
    name: str
    role: Role

    class Config:
        orm_mode = True


class RepositoryUserRole(enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "administrator"


class RepositoryUserPermission(enum.Enum):
    READ = "read"
    WRITE = "write"


class RepositoryUser(BaseModel):
    username: str
    role: RepositoryUserRole
    permission: RepositoryUserPermission

    class Config:
        orm_mode = True


class PatchRepositoryUser(BaseModel):
    role: t.Optional[RepositoryUserRole]
    password: t.Optional[str]
    permission: t.Optional[RepositoryUserPermission]


class ProjectUserAssociation(Base):
    __tablename__ = "project_user_association"

    username = Column(ForeignKey("users.name"), primary_key=True)
    projects_name = Column(ForeignKey("projects.name"), primary_key=True)
    user = relationship("DatabaseUser", back_populates="projects")
    projects = relationship("DatabaseProject", back_populates="users")
    permission = Column(Enum(RepositoryUserPermission), nullable=False)
    role = Column(Enum(RepositoryUserRole))
