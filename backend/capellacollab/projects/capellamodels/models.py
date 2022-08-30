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

# 1st party:
# Import required for sqlalchemy
import capellacollab.projects.users.models
from capellacollab.core.database import Base


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class CapellaModelType(enum.Enum):
    PROJECT = "project"
    LIBRARY = "library"


class DB_CapellaModel(Base):
    __tablename__ = "capella_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    editing_mode = Column(Enum(EditingMode))
    model_type = Column(Enum(CapellaModelType))
    project = relationship("DatabaseProject", back_populates="models")
    project_name = Column(String, ForeignKey("projects.name"))
    t4c_model = relationship("DB_T4CModel", back_populates="model")
    git_model = relationship("DB_GitModel", back_populates="model")


class NewModel(BaseModel):
    name: str
    description: t.Optional[str]
    tool_id: int
    version_id: int
    type_id: int


class ResponseModel(BaseModel):
    id: int
    project_slug: str
    name: str
    description: str

    @classmethod
    def from_model(cls, model: DB_CapellaModel):
        return cls(
            id=model.id,
            project_slug=model.project.slug,
            name=model.name,
            description=model.description,
        )
