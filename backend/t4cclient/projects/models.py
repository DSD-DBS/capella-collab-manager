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
import t4cclient.projects.users.models
from t4cclient.core.database import Base


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class ProjectType(enum.Enum):
    PROJECT = "project"
    LIBRARY = "library"


class Warning(enum.Enum):
    LICENCE_LIMIT = "LICENCE_LIMIT"
    NO_GIT_MODEL_DEFINED = "NO_GIT_MODEL_DEFINED"


class GetProject(BaseModel):
    name: str
    description: str
    editing_mode: EditingMode
    type: ProjectType

    class Config:
        orm_mode = True


class PostRepositoryRequest(BaseModel):
    name: str


class DatabaseProject(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    editing_mode = Column(Enum(EditingMode))
    project_type = Column(Enum(ProjectType))
    users = relationship(
        "RepositoryUserAssociation",
        back_populates="projects",
    )
    t4c_models = relationship("DatabaseT4CModel", back_populates="project")
    git_models = relationship("DB_GitModel", back_populates="project")
