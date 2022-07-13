import enum
from pydantic import BaseModel
from slugify import slugify
from sqlalchemy import (Column, Enum, ForeignKey, Integer, String,
    UniqueConstraint)
from sqlalchemy.orm import relationship
import typing as t

from capellacollab.core.database import Base
from capellacollab.projects.models import DatabaseProject
from capellacollab.tools.models import Tool, Type, Version


class NewModel(BaseModel):
    name: str
    description: str | None
    tool_id: int
    version_id: int
    type_id: int


class Model(Base):
    __tablename__ = 'models'
    __table_args__ = (
        UniqueConstraint('project_id', 'slug'),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String)
    description = Column(String)

    project_id = Column(Integer, ForeignKey(DatabaseProject.id))
    project = relationship("DatabaseProject", back_populates="models")

    tool_id = Column(Integer, ForeignKey(Tool.id))
    tool = relationship(Tool)

    version_id = Column(Integer, ForeignKey(Version.id))
    version = relationship(Version)

    type_id = Column(Integer, ForeignKey(Type.id))
    tool_type = relationship(Type)


class ResponseModel(BaseModel):
    slug: str
    project_slug: str
    name: str
    description: str
    tool_id: int
    version_id: int
    type_id: int

    @classmethod
    def from_model(cls, model: Model):
        return cls(
            slug = model.slug,
            project_slug = model.project.slug,
            name = model.name,
            description = model.description,
            tool_id = model.tool_id,
            version_id = model.version_id,
            type_id = model.type_id,
        )
