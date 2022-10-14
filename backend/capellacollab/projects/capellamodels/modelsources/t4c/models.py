# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.settings.modelsources.t4c.repositories.models import (
    BaseT4CRepository,
    T4CRepositoryWithInstance,
)


class DatabaseT4CModel(Base):
    __tablename__ = "t4c_models"
    __table_args__ = (UniqueConstraint("repository_id", "name"),)

    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)

    repository_id = Column(Integer, ForeignKey("t4c_repositories.id"))
    repository = relationship("DatabaseT4CRepository", back_populates="models")

    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship("DatabaseCapellaModel", back_populates="t4c_models")


class CreateT4CModel(BaseModel):
    name: str
    t4c_instance_id: int
    t4c_repository_id: int


class ResponseT4CModel(BaseModel):
    id: int
    name: str
    repository: T4CRepositoryWithInstance

    class Config:
        orm_mode = True


class T4CRepositoryWithModels(BaseT4CRepository):
    models: list[T4CModel]

    class Config:
        orm_mode = True
