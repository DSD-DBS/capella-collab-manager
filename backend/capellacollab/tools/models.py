# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base

from .integrations.models import ToolIntegrations

if t.TYPE_CHECKING:
    from .integrations.models import DatabaseToolIntegrations


class Tool(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str | None]
    docker_image_template: Mapped[str]
    docker_image_backup_template: Mapped[str | None]
    readonly_docker_image_template: Mapped[str | None]

    versions: Mapped[list[Version]] = relationship(back_populates="tool")
    natures: Mapped[list[Nature]] = relationship(back_populates="tool")

    integrations: Mapped[DatabaseToolIntegrations] = relationship(
        back_populates="tool", uselist=False
    )


class Version(Base):
    __tablename__ = "versions"
    __table_args__ = (UniqueConstraint("tool_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]
    is_recommended: Mapped[bool]
    is_deprecated: Mapped[bool]

    tool_id: Mapped[int | None] = mapped_column(ForeignKey(Tool.id))
    tool: Mapped[Tool] = relationship(back_populates="versions")


class Nature(Base):
    __tablename__ = "types"
    __table_args__ = (UniqueConstraint("tool_id", "name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    tool_id: Mapped[int | None] = mapped_column(ForeignKey(Tool.id))
    tool: Mapped[Tool] = relationship(back_populates="natures")


class ToolBase(BaseModel):
    id: int
    name: str
    integrations: ToolIntegrations

    class Config:
        orm_mode = True


class ToolDockerimage(BaseModel):
    persistent: str
    readonly: str | None
    backup: str | None

    @classmethod
    def from_orm(cls, obj: Tool) -> ToolDockerimage:
        return ToolDockerimage(
            persistent=obj.docker_image_template,
            readonly=obj.readonly_docker_image_template,
            backup=obj.docker_image_backup_template,
        )

    class Config:
        orm_mode = True


class PatchToolDockerimage(BaseModel):
    persistent: str | None
    readonly: str | None
    backup: str | None


class CreateToolVersion(BaseModel):
    name: str


class CreateToolNature(BaseModel):
    name: str


class UpdateToolVersion(BaseModel):
    name: str | None
    is_recommended: bool | None
    is_deprecated: bool | None


class ToolVersionBase(BaseModel):
    id: int
    name: str
    is_recommended: bool
    is_deprecated: bool

    class Config:
        orm_mode = True


class ToolVersionWithTool(ToolVersionBase):
    tool: ToolBase


class ToolNatureBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CreateTool(BaseModel):
    name: str
