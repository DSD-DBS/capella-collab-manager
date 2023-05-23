# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base
from capellacollab.settings.modelsources.t4c.models import (
    DatabaseT4CInstance,
    T4CInstance,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.modelsources.t4c.models import (
        DatabaseT4CModel,
    )


class DatabaseT4CRepository(Base):
    __tablename__ = "t4c_repositories"
    __table_args__ = (UniqueConstraint("instance_id", "name"),)

    id: Mapped[int] = mapped_column(
        primary_key=True, index=True, autoincrement=True, unique=True
    )
    name: Mapped[str]

    instance_id: Mapped[int] = mapped_column(ForeignKey("t4c_instances.id"))
    instance: Mapped[DatabaseT4CInstance] = relationship(
        back_populates="repositories"
    )

    models: Mapped[list[DatabaseT4CModel]] = relationship(
        back_populates="repository", cascade="all, delete"
    )


class CreateT4CRepository(BaseModel):
    name: str


class T4CRepositoryStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    INSTANCE_UNREACHABLE = "INSTANCE_UNREACHABLE"
    NOT_FOUND = "NOT_FOUND"
    INITIAL = "INITIAL"


class T4CInstanceWithRepositories(T4CInstance):
    repositories: list[T4CRepository]

    class Config:
        orm_mode = True


class T4CRepository(CreateT4CRepository):
    id: int
    instance: T4CInstance
    status: T4CRepositoryStatus | None

    class Config:
        orm_mode = True


T4CInstanceWithRepositories.update_forward_refs()
