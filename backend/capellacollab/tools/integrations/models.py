# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    from capellacollab.tools.models import Tool


class ToolIntegrations(BaseModel):
    t4c: bool
    pure_variants: bool

    class Config:
        orm_mode = True


class PatchToolIntegrations(BaseModel):
    t4c: t.Optional[bool]
    pure_variants: t.Optional[bool]


class DatabaseToolIntegrations(Base):
    __tablename__ = "tool_integrations"

    id: int = Column(Integer, primary_key=True)

    tool_id: str = Column(Integer, ForeignKey("tools.id"))
    tool: Tool = relationship("Tool", back_populates="integrations")

    t4c: bool = Column(Boolean, default=False)
    pure_variants: bool = Column(Boolean, default=False)
