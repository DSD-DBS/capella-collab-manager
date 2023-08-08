# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseToolModel


class ToolModelRestrictions(pydantic.BaseModel):
    # If true, access to the specific resource is granted for a model.
    # If false, the access is not allowed.

    allow_pure_variants: bool

    class Config:
        orm_mode = True


class DatabaseToolModelRestrictions(database.Base):
    __tablename__ = "model_restrictions"

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, unique=True
    )

    model_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("models.id"))
    model: orm.Mapped[DatabaseToolModel] = orm.relationship(
        back_populates="restrictions"
    )

    allow_pure_variants: orm.Mapped[bool] = orm.mapped_column(default=False)
