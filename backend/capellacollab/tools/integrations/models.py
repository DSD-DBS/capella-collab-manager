# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.tools.models import Tool


class ToolIntegrations(pydantic.BaseModel):
    t4c: bool
    pure_variants: bool
    jupyter: bool

    class Config:
        orm_mode = True


class PatchToolIntegrations(pydantic.BaseModel):
    t4c: bool | None
    pure_variants: bool | None
    jupyter: bool | None


class DatabaseToolIntegrations(database.Base):
    __tablename__ = "tool_integrations"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    tool_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("tools.id"))
    tool: orm.Mapped[Tool] = orm.relationship(back_populates="integrations")

    t4c: orm.Mapped[bool] = orm.mapped_column(default=False)
    pure_variants: orm.Mapped[bool] = orm.mapped_column(default=False)
    jupyter: orm.Mapped[bool] = orm.mapped_column(default=False)
