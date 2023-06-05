# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.tools.integrations import models as integrations_models

if t.TYPE_CHECKING:
    from .integrations.models import DatabaseToolIntegrations


class Tool(database.Base):
    __tablename__ = "tools"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    name: orm.Mapped[str | None]
    docker_image_template: orm.Mapped[str]
    docker_image_backup_template: orm.Mapped[str | None]
    readonly_docker_image_template: orm.Mapped[str | None]

    versions: orm.Mapped[list[Version]] = orm.relationship(
        back_populates="tool"
    )
    natures: orm.Mapped[list[Nature]] = orm.relationship(back_populates="tool")

    integrations: orm.Mapped[DatabaseToolIntegrations] = orm.relationship(
        back_populates="tool", uselist=False
    )


class Version(database.Base):
    __tablename__ = "versions"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    name: orm.Mapped[str]
    is_recommended: orm.Mapped[bool]
    is_deprecated: orm.Mapped[bool]

    tool_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("tools.id")
    )
    tool: orm.Mapped[Tool] = orm.relationship(back_populates="versions")


class Nature(database.Base):
    __tablename__ = "types"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str]

    tool_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("tools.id")
    )
    tool: orm.Mapped[Tool] = orm.relationship(back_populates="natures")


class ToolBase(pydantic.BaseModel):
    id: int
    name: str
    integrations: integrations_models.ToolIntegrations

    class Config:
        orm_mode = True


class ToolDockerimage(pydantic.BaseModel):
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


class PatchToolDockerimage(pydantic.BaseModel):
    persistent: str | None
    readonly: str | None
    backup: str | None


class CreateToolVersion(pydantic.BaseModel):
    name: str


class CreateToolNature(pydantic.BaseModel):
    name: str


class UpdateToolVersion(pydantic.BaseModel):
    name: str | None
    is_recommended: bool | None
    is_deprecated: bool | None


class ToolVersionBase(pydantic.BaseModel):
    id: int
    name: str
    is_recommended: bool
    is_deprecated: bool

    class Config:
        orm_mode = True


class ToolVersionWithTool(ToolVersionBase):
    tool: ToolBase


class ToolNatureBase(pydantic.BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class CreateTool(pydantic.BaseModel):
    name: str
