# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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


class DatabaseTool(database.Base):
    __tablename__ = "tools"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    name: orm.Mapped[str]
    slug: orm.Mapped[str]
    docker_image_template: orm.Mapped[str]
    docker_image_backup_template: orm.Mapped[str | None]
    readonly_docker_image_template: orm.Mapped[str | None]

    versions: orm.Mapped[list[DatabaseVersion]] = orm.relationship(
        back_populates="tool"
    )
    natures: orm.Mapped[list[DatabaseNature]] = orm.relationship(
        back_populates="tool"
    )

    integrations: orm.Mapped[DatabaseToolIntegrations] = orm.relationship(
        back_populates="tool", uselist=False
    )


class DatabaseVersion(database.Base):
    __tablename__ = "versions"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    name: orm.Mapped[str]
    slug: orm.Mapped[str] = orm.mapped_column(nullable=False)
    is_recommended: orm.Mapped[bool]
    is_deprecated: orm.Mapped[bool]

    tool_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("tools.id")
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(
        back_populates="versions"
    )


class DatabaseNature(database.Base):
    __tablename__ = "types"
    __table_args__ = (sa.UniqueConstraint("tool_id", "name"),)

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    name: orm.Mapped[str]

    tool_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("tools.id")
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(back_populates="natures")


class ToolBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    integrations: integrations_models.ToolIntegrations


class ToolDockerimage(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    persistent: str = pydantic.Field(
        ..., validation_alias="docker_image_template"
    )
    readonly: str | None = pydantic.Field(
        None, validation_alias="readonly_docker_image_template"
    )
    backup: str | None = pydantic.Field(
        None, validation_alias="docker_image_backup_template"
    )


class PatchToolDockerimage(pydantic.BaseModel):
    persistent: str | None = None
    readonly: str | None = None
    backup: str | None = None


class CreateToolVersion(pydantic.BaseModel):
    name: str


class CreateToolNature(pydantic.BaseModel):
    name: str


class UpdateToolVersion(pydantic.BaseModel):
    name: str | None = None
    is_recommended: bool | None = None
    is_deprecated: bool | None = None


class ToolVersionBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    is_recommended: bool
    is_deprecated: bool


class ToolVersionWithTool(ToolVersionBase):
    tool: ToolBase


class ToolNatureBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str


class CreateTool(pydantic.BaseModel):
    name: str
