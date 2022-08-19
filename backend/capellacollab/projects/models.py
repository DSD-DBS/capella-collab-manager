# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
import enum
import typing as t

# 1st party:
# Import required for sqlalchemy
import capellacollab.projects.users.models
from capellacollab.core.database import Base

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Warning(enum.Enum):
    LICENCE_LIMIT = "LICENCE_LIMIT"
    NO_GIT_MODEL_DEFINED = "NO_GIT_MODEL_DEFINED"


class UserMetadata(BaseModel):
    leads: int
    contributors: int
    subscribers: int


class Project(BaseModel):
    name: str
    slug: str
    staged_by: str | None
    description: t.Optional[str]
    users: UserMetadata

    class Config:
        orm_mode = True


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
    staged_by = Column(String)
    description = Column(String)
    users = relationship(
        "ProjectUserAssociation",
        back_populates="projects",
    )
    models = relationship("DB_Model", back_populates="project")
