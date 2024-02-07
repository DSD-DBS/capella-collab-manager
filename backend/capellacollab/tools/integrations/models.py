# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.tools.models import DatabaseTool


class ToolIntegrations(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    t4c: bool
    pure_variants: bool
    jupyter: bool


class PatchToolIntegrations(pydantic.BaseModel):
    t4c: bool | None = None
    pure_variants: bool | None = None
    jupyter: bool | None = None


class DatabaseToolIntegrations(database.Base):
    __tablename__ = "tool_integrations"

    id: orm.Mapped[int] = orm.mapped_column(init=False, primary_key=True)

    tool_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("tools.id"), init=False
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship(
        back_populates="integrations"
    )

    t4c: orm.Mapped[bool] = orm.mapped_column(default=False)
    pure_variants: orm.Mapped[bool] = orm.mapped_column(default=False)
    jupyter: orm.Mapped[bool] = orm.mapped_column(default=False)
