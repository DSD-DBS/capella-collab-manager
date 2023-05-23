# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base
from capellacollab.settings.modelsources.t4c.repositories.models import (
    T4CRepository,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
    from capellacollab.settings.modelsources.t4c.repositories.models import (
        DatabaseT4CRepository,
    )


class DatabaseT4CModel(Base):
    __tablename__ = "t4c_models"
    __table_args__ = (UniqueConstraint("repository_id", "model_id", "name"),)

    id: Mapped[int] = mapped_column(unique=True, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)

    repository_id: Mapped[int] = mapped_column(
        ForeignKey("t4c_repositories.id")
    )
    repository: Mapped[DatabaseT4CRepository] = relationship(
        back_populates="models"
    )

    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    model: Mapped[DatabaseCapellaModel] = relationship(
        back_populates="t4c_models"
    )


class SubmitT4CModel(BaseModel):
    name: str
    t4c_instance_id: int
    t4c_repository_id: int


class SimpleT4CModel(BaseModel):
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


class T4CModel(BaseModel):
    id: int
    name: str
    repository: T4CRepository

    class Config:
        orm_mode = True


class T4CRepositoryWithModels(T4CRepository):
    models: list[T4CModel]

    class Config:
        orm_mode = True
