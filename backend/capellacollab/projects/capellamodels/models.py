# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import enum
import typing as t

# 1st party:
from capellacollab.core.database import Base
from capellacollab.tools.models import Tool, Type, Version

# 3rd party:
from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class CapellaModelType(enum.Enum):
    PROJECT = "project"
    LIBRARY = "library"


class NewModel(BaseModel):
    name: str
    description: str | None
    tool_id: int


class EmptyModel(BaseModel):
    name: str
    description: str | None
    tool_id: int
    version_id: int
    type_id: int


class ToolDetails(BaseModel):
    version_id: int
    type_id: int


class DB_Model(Base):
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
    def from_empty_model(cls, new_model: EmptyModel, project):
        return cls(
            name=new_model.name,
            slug=slugify(new_model.name),
            description=new_model.description,
            tool_id=new_model.tool_id,
            version_id=new_model.version_id,
            type_id=new_model.type_id,
            project_id=project.id,
        )

    @classmethod
    def from_new_model(cls, new_model: NewModel, project):
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
    def from_model(cls, model: DB_Model):
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
