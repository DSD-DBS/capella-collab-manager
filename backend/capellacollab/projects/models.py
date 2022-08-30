# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
import enum
import typing as t

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# 1st party:
# Import required for sqlalchemy
import capellacollab.projects.users.models
from capellacollab.core.database import Base
from capellacollab.projects.users.models import RepositoryUser


class Warning(enum.Enum):
    LICENCE_LIMIT = "LICENCE_LIMIT"
    NO_GIT_MODEL_DEFINED = "NO_GIT_MODEL_DEFINED"


class UserMetadata(BaseModel):
    leads: int
    contributors: int
    subscribers: int


class Username(BaseModel):
    name: str

    class Config:
        orm_mode = True


class Project(BaseModel):
    name: str
    slug: str
    staged_by: Username | None
    description: str | None
    users_metadata: UserMetadata | None

    class Config:
        orm_mode = True


class ProjectWithUsers(Project):
    users: list[RepositoryUser]


class PatchProject(BaseModel):
    description: str


class PostRepositoryRequest(BaseModel):
    name: str
    description: str | None


class DatabaseProject(Base):
    __tablename__ = "projects"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)
    staged_by_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)

    users = relationship(
        "ProjectUserAssociation",
        back_populates="projects",
        cascade="all, delete",
    )
    models = relationship(
        "DB_Model",
        back_populates="project",
        cascade="all, delete",
    )
    staged_by = relationship("DatabaseUser", back_populates="stages")
