# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.tools.models import DatabaseTool


class ToolIntegrations(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    t4c: bool = Field(description="Status of the tool integration with T4C")
    pure_variants: bool = Field(
        description="Status of the tool integration with Pure Variants"
    )
    jupyter: bool = Field(
        description="Status of the tool integration with Jupyter"
    )


class PatchToolIntegrations(BaseModel):
    t4c: bool | None = Field(
        default=None,
        description="Indicator of whether the tool is integrated with T4C provided for patching",
    )
    pure_variants: bool | None = Field(
        default=None,
        description="Indicator of whether the tool is integrated with Pure Variants for patching",
    )
    jupyter: bool | None = Field(
        default=None,
        description="Indicator of whether the tool is integrated with Jupyter for patching",
    )


class DatabaseToolIntegrations(database.Base):
    __tablename__ = "tool_integrations"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    tool_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("tools.id"))
    tool: orm.Mapped[DatabaseTool] = orm.relationship(
        back_populates="integrations"
    )

    t4c: orm.Mapped[bool] = orm.mapped_column(default=False)
    pure_variants: orm.Mapped[bool] = orm.mapped_column(default=False)
    jupyter: orm.Mapped[bool] = orm.mapped_column(default=False)
