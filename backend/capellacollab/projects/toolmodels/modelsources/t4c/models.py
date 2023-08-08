# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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
    model: orm.Mapped[DatabaseToolModel] = orm.relationship(
        back_populates="t4c_models"
    )


class SubmitT4CModel(pydantic.BaseModel):
    name: str
    t4c_instance_id: int
    t4c_repository_id: int


class SimpleT4CModel(pydantic.BaseModel):
    project_name: str
    repository_name: str
    instance_name: str

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj: DatabaseT4CModel) -> SimpleT4CModel:
        return SimpleT4CModel(
            project_name=obj.name,
            repository_name=obj.repository.name,
            instance_name=obj.repository.instance.name,
        )


class T4CModel(pydantic.BaseModel):
    id: int
    name: str
    repository: repositories_models.T4CRepository

    class Config:
        orm_mode = True


class T4CRepositoryWithModels(repositories_models.T4CRepository):
    models: list[T4CModel]

    class Config:
        orm_mode = True
