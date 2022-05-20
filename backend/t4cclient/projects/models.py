# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Standard library:
import enum
import typing as t

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# local:
# Import required for sqlalchemy
import t4cclient.projects.capellamodels.models
import t4cclient.projects.users.models
from t4cclient.core.database import Base


class Warning(enum.Enum):
    LICENCE_LIMIT = "LICENCE_LIMIT"
    NO_GIT_MODEL_DEFINED = "NO_GIT_MODEL_DEFINED"


class UserMetadata(BaseModel):
    leads: int
    contributors: int
    subscribers: int


class Project(BaseModel):
    name: str
    description: t.Optional[str]
    users: UserMetadata

    class Config:
        orm_mode = True


class PostRepositoryRequest(BaseModel):
    name: str


class DatabaseProject(Base):
    __tablename__ = "projects"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    users = relationship(
        "ProjectUserAssociation",
        back_populates="projects",
    )
    models = relationship("DB_CapellaModel", back_populates="project")
