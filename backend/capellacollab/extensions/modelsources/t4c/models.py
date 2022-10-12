# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.settings.modelsources.t4c.repositories.models import (
    DatabaseT4CRepository,
)


class DatabaseT4CModel(Base):
    __tablename__ = "t4c_models"
    __table_args__ = (UniqueConstraint("repository_id", "name"),)

    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)

    repository_id = Column(Integer, ForeignKey("t4c_repositories.id"))
    repository = relationship("DatabaseT4CRepository", back_populates="models")

    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship("DatabaseCapellaModel", back_populates="t4c_model")


class CreateT4CModel(BaseModel):
    name: str
    t4c_instance_id: int
    t4c_repository_id: int
