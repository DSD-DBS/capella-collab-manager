# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.settings.modelsources.t4c.repositories import (
    models as repositories_models,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
    from capellacollab.settings.modelsources.t4c.repositories.models import (
        DatabaseT4CRepository,
    )


class DatabaseT4CModel(database.Base):
    __tablename__ = "t4c_models"
    __table_args__ = (
        sa.UniqueConstraint("repository_id", "model_id", "name"),
    )

    id: orm.Mapped[int] = orm.mapped_column(
        unique=True, primary_key=True, index=True
    )
    name: orm.Mapped[str] = orm.mapped_column(index=True)

    repository_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("t4c_repositories.id")
    )
    repository: orm.Mapped[DatabaseT4CRepository] = orm.relationship(
        back_populates="models"
    )

    model_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("models.id"))
    model: orm.Mapped[DatabaseCapellaModel] = orm.relationship(
        back_populates="t4c_models"
    )


class SubmitT4CModel(pydantic.BaseModel):
    name: str
    t4c_instance_id: int
    t4c_repository_id: int


class SimpleT4CModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

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


class T4CModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    name: str
    repository: repositories_models.T4CRepository


class T4CRepositoryWithModels(repositories_models.T4CRepository):
    model_config = pydantic.ConfigDict(from_attributes=True)

    models: list[T4CModel]
