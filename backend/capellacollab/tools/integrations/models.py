# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    from capellacollab.tools.models import Tool


class ToolIntegrations(BaseModel):
    t4c: bool
    pure_variants: bool
    jupyter: bool

    class Config:
        orm_mode = True


class PatchToolIntegrations(BaseModel):
    t4c: bool | None
    pure_variants: bool | None
    jupyter: bool | None


class DatabaseToolIntegrations(Base):
    __tablename__ = "tool_integrations"

    id: Mapped[int] = mapped_column(primary_key=True)

    tool_id: Mapped[int] = mapped_column(ForeignKey("tools.id"))
    tool: Mapped[Tool] = relationship(back_populates="integrations")

    t4c: Mapped[bool] = mapped_column(default=False)
    pure_variants: Mapped[bool] = mapped_column(default=False)
    jupyter: Mapped[bool] = mapped_column(default=False)
