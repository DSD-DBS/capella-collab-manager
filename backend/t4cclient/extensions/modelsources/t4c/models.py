# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# local:
from t4cclient.core.database import Base


class DB_T4CModel(Base):
    __tablename__ = "t4c_models"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String, index=True)
    model_id = Column(Integer, ForeignKey("capella_models.id"))
    model = relationship("DB_CapellaModel", back_populates="t4c_model")


class RepositoryProjectBase(BaseModel):
    name: str

    class Config:
        orm_mode = True


class RepositoryProject(RepositoryProjectBase):
    id: int
    repository_name: str
