# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.core.models import ResponseModel
from capellacollab.settings.modelsources.t4c.models import T4CInstance


class DatabaseT4CRepository(Base):
    __tablename__ = "t4c_repositories"
    __table_args__ = (UniqueConstraint("instance_id", "name"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    instance_id = Column(
        Integer, ForeignKey("t4c_instances.id"), nullable=False
    )

    instance = relationship(
        "DatabaseT4CInstance", back_populates="repositories"
    )


class CreateT4CRepository(BaseModel):
    name: str


class T4CRepositoryStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    INSTANCE_UNREACHABLE = "INSTANCE_UNREACHABLE"
    NOT_FOUND = "NOT_FOUND"
    INITIAL = "INITIAL"


class T4CRepositories(ResponseModel):
    payload: t.List[T4CRepository]


class T4CInstanceWithRepositories(T4CInstance):
    repositories: list[T4CRepository]

    class Config:
        orm_mode = True


class T4CRepository(CreateT4CRepository):
    id: int
    instance: T4CInstance
    status: t.Optional[T4CRepositoryStatus]

    class Config:
        orm_mode = True
