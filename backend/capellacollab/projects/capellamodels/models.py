# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

# Import required for sqlalchemy
import capellacollab.projects.users.models
from capellacollab.core.database import Base
from capellacollab.tools.models import Tool, Type, Version


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class CapellaModelType(enum.Enum):
    PROJECT = "project"
    LIBRARY = "library"


class CapellaModel(BaseModel):
    name: str
    description: t.Optional[str]
    tool_id: int


class EmptyModel(BaseModel):
    name: str
    description: t.Optional[str]
    tool_id: int
    version_id: int
    type_id: int


class ToolDetails(BaseModel):
    version_id: int
    type_id: int


class DatabaseCapellaModel(Base):
    __tablename__ = "models"
    __table_args__ = (UniqueConstraint("project_id", "slug"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String)

    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("DatabaseProject", back_populates="models")

    tool_id = Column(Integer, ForeignKey(Tool.id))
    tool = relationship(Tool)

    version_id = Column(Integer, ForeignKey(Version.id))
    version = relationship(Version)

    type_id = Column(Integer, ForeignKey(Type.id))
    tool_type = relationship(Type)

    editing_mode = Column(Enum(EditingMode))
    model_type = Column(Enum(CapellaModelType))

    t4c_model = relationship("DB_T4CModel", back_populates="model")
    git_model = relationship("DB_GitModel", back_populates="model")

    @classmethod
    def from_new_model(cls, new_model: CapellaModel, project):
        return cls(
            name=new_model.name,
            slug=slugify(new_model.name),
            description=new_model.description,
            project_id=project.id,
            tool_id=new_model.tool_id,
        )


class ResponseModel(BaseModel):
    id: int
    slug: str
    project_slug: str
    name: str
    description: str
    tool_id: t.Optional[int]
    version_id: t.Optional[int]
    type_id: t.Optional[int]
    t4c_model: t.Optional[int]
    git_model: t.Optional[int]

    @classmethod
    def from_model(cls, model: DatabaseCapellaModel):
        return cls(
            id=model.id,
            slug=model.slug,
            project_slug=model.project.slug,
            name=model.name,
            description=model.description,
            tool_id=model.tool_id,
            version_id=model.version_id,
            type_id=model.type_id,
        )
