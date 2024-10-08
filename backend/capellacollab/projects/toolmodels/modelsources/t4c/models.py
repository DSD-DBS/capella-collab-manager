# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    models as repositories_models,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseToolModel
    from capellacollab.settings.modelsources.t4c.instance.repositories.models import (
        DatabaseT4CRepository,
    )


class DatabaseT4CModel(database.Base):
    __tablename__ = "t4c_models"
    __table_args__ = (
        sa.UniqueConstraint("repository_id", "model_id", "name"),
    )

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, unique=True, primary_key=True, index=True
    )
    name: orm.Mapped[str] = orm.mapped_column(index=True)

    repository_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("t4c_repositories.id"), init=False
    )
    repository: orm.Mapped[DatabaseT4CRepository] = orm.relationship(
        back_populates="integrations"
    )

    model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("models.id"), init=False
    )
    model: orm.Mapped[DatabaseToolModel] = orm.relationship(
        back_populates="t4c_models"
    )


class SubmitT4CModel(core_pydantic.BaseModel):
    name: str
    t4c_instance_id: int
    t4c_repository_id: int


class PatchT4CModel(core_pydantic.BaseModel):
    name: str | None = None
    t4c_instance_id: int | None = None
    t4c_repository_id: int | None = None


class SimpleT4CModelWithRepository(core_pydantic.BaseModel):
    id: int
    name: str
    repository: repositories_models.SimpleT4CRepository
