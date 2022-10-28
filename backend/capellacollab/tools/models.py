# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base


class Tool(Base):
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    docker_image_template = Column(String)

    versions = relationship("Version", back_populates="tool")
    natures = relationship("Nature", back_populates="tool")


class Version(Base):
    __tablename__ = "versions"
    __table_args__ = (UniqueConstraint("tool_id", "name"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_recommended = Column(Boolean)
    is_deprecated = Column(Boolean)

    tool_id = Column(Integer, ForeignKey(Tool.id))
    tool: Tool = relationship("Tool", back_populates="versions")


class Nature(Base):
    __tablename__ = "types"
    __table_args__ = (UniqueConstraint("tool_id", "name"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)

    tool_id = Column(Integer, ForeignKey(Tool.id))
    tool = relationship("Tool", back_populates="natures")


class ToolBase(BaseModel):
    id: int
    name: str
    docker_image_template: str

    class Config:
        orm_mode = True


class ToolDockerimage(BaseModel):
    persistent: str
    readonly: str

    @classmethod
    def from_orm(cls, obj: Tool) -> ToolDockerimage:
        return ToolDockerimage(
            persistent=obj.docker_image_template,
            readonly=obj.docker_image_template,
        )

    class Config:
        orm_mode = True


class PatchToolDockerimage(BaseModel):
    persistent: t.Optional[str]
    readonly: t.Optional[str]


class CreateToolVersion(BaseModel):
    name: str


class CreateToolNature(BaseModel):
    name: str


class UpdateToolVersion(BaseModel):
    name: t.Optional[str]
    is_recommended: t.Optional[bool]
    is_deprecated: t.Optional[bool]


class ToolVersionBase(BaseModel):
    id: int
    name: str
    is_recommended: bool
    is_deprecated: bool

    class Config:
        orm_mode = True


class ToolNatureBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CreateTool(BaseModel):
    name: str
