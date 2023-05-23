# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base
from capellacollab.projects.toolmodels.modelsources.git.models import GitModel
from capellacollab.projects.toolmodels.modelsources.t4c.models import T4CModel
from capellacollab.tools.models import (
    Nature,
    Tool,
    ToolBase,
    ToolNatureBase,
    ToolVersionBase,
    Version,
)

from .restrictions.models import (
    DatabaseToolModelRestrictions,
    ToolModelRestrictions,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.projects.toolmodels.modelsources.git.models import (
        DatabaseGitModel,
    )
    from capellacollab.projects.toolmodels.modelsources.t4c.models import (
        DatabaseT4CModel,
    )


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class PostCapellaModel(BaseModel):
    name: str
    description: str | None
    tool_id: int


class PatchCapellaModel(BaseModel):
    description: str | None
    version_id: int
    nature_id: int


class ToolDetails(BaseModel):
    version_id: int
    nature_id: int


class DatabaseCapellaModel(Base):
    __tablename__ = "models"
    __table_args__ = (UniqueConstraint("project_id", "slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True, unique=True)

    name: Mapped[str] = mapped_column(index=True)
    slug: Mapped[str]
    description: Mapped[str]

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped[DatabaseProject] = relationship(back_populates="models")

    tool_id: Mapped[int] = mapped_column(ForeignKey(Tool.id))
    tool: Mapped[Tool] = relationship()

    version_id: Mapped[int | None] = mapped_column(ForeignKey(Version.id))
    version: Mapped[Version] = relationship()

    nature_id: Mapped[int | None] = mapped_column(ForeignKey(Nature.id))
    nature: Mapped[Nature] = relationship()

    editing_mode: Mapped[EditingMode | None]

    t4c_models: Mapped[list[DatabaseT4CModel]] = relationship(
        back_populates="model"
    )
    git_models: Mapped[list[DatabaseGitModel]] = relationship(
        back_populates="model"
    )

    restrictions: Mapped[DatabaseToolModelRestrictions] = relationship(
        back_populates="model", uselist=False
    )


class CapellaModel(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    tool: ToolBase
    version: ToolVersionBase | None
    nature: ToolNatureBase | None
    git_models: list[GitModel] | None
    t4c_models: list[T4CModel] | None

    restrictions: ToolModelRestrictions | None

    class Config:
        orm_mode = True
