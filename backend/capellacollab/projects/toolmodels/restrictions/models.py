# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import Boolean, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel


class ToolModelRestrictions(BaseModel):
    # If true, access to the specific resource is granted for a model.
    # If false, the access is not allowed.

    allow_pure_variants: bool

    class Config:
        orm_mode = True


class DatabaseToolModelRestrictions(Base):
    __tablename__ = "model_restrictions"

    id: int = Column(Integer, primary_key=True, index=True, unique=True)

    model_id: int = Column(Integer, ForeignKey("models.id"))
    model: DatabaseCapellaModel = relationship(
        "DatabaseCapellaModel", back_populates="restrictions"
    )

    allow_pure_variants: bool = Column(Boolean, default=False, nullable=False)
