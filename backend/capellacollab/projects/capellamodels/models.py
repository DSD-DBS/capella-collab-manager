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
from capellacollab.tools.models import (
    Tool,
    ToolBase,
    ToolTypeBase,
    ToolVersionBase,
    Type,
    Version,
)


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class CapellaModel(BaseModel):
    name: str
    description: t.Optional[str]
    tool_id: int


class ToolDetails(BaseModel):
    version_id: int
    type_id: int


class DatabaseCapellaModel(Base):
    __tablename__ = "models"
    __table_args__ = (UniqueConstraint("project_id", "slug"),)

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, index=True)
    slug = Column(String, nullable=False)
    description = Column(String)

    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("DatabaseProject", back_populates="models")

    tool_id = Column(Integer, ForeignKey(Tool.id))
    tool = relationship(Tool)

    version_id = Column(Integer, ForeignKey(Version.id))
    version = relationship(Version)

    type_id = Column(Integer, ForeignKey(Type.id))
    type = relationship(Type)

    editing_mode = Column(Enum(EditingMode))

    t4c_model = relationship("DB_T4CModel", back_populates="model")
    git_model = relationship("DB_GitModel", back_populates="model")


class ResponseModel(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    tool: ToolBase
    version: t.Optional[ToolVersionBase]
    type: t.Optional[ToolTypeBase]
    t4c_model_id: t.Optional[int]
    git_model_id: t.Optional[int]

    class Config:
        orm_mode = True
