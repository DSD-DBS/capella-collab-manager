# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseToolModel


class ToolModelRestrictions(core_pydantic.BaseModel):
    # If true, access to the specific resource is granted for a model.
    # If false, the access is not allowed.

    allow_pure_variants: bool


class DatabaseToolModelRestrictions(database.Base):
    __tablename__ = "model_restrictions"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, unique=True
    )

    model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("models.id"), init=False
    )
    model: orm.Mapped[DatabaseToolModel] = orm.relationship(
        back_populates="restrictions"
    )

    allow_pure_variants: orm.Mapped[bool] = orm.mapped_column(default=False)
