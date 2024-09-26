# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.settings.modelsources.t4c.repositories import (
    models as repositories_models,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseToolModel
    from capellacollab.settings.modelsources.t4c.repositories.models import (
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
        back_populates="models"
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


class SimpleT4CModel(core_pydantic.BaseModel):
    project_name: str
    repository_name: str
    instance_name: str

    @pydantic.model_validator(mode="before")
    @classmethod
    def transform_database_t4c_model(cls, data: t.Any) -> t.Any:
        if isinstance(data, DatabaseT4CModel):
            return SimpleT4CModel(
                project_name=data.name,
                repository_name=data.repository.name,
                instance_name=data.repository.instance.name,
            )
        return data


class T4CModel(core_pydantic.BaseModel):
    id: int
    name: str
    repository: repositories_models.T4CRepository


class T4CRepositoryWithModels(repositories_models.T4CRepository):
    models: list[T4CModel]
