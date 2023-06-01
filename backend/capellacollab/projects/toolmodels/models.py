# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

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


class PostCapellaModel(pydantic.BaseModel):
    name: str
    description: str | None
    tool_id: int


class PatchCapellaModel(pydantic.BaseModel):
    description: str | None
    version_id: int
    nature_id: int


class ToolDetails(pydantic.BaseModel):
    version_id: int
    nature_id: int


class DatabaseCapellaModel(Base):
    __tablename__ = "models"
    __table_args__ = (sa.UniqueConstraint("project_id", "slug"),)

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, unique=True
    )

    name: orm.Mapped[str] = orm.mapped_column(index=True)
    slug: orm.Mapped[str]
    description: orm.Mapped[str]

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id")
    )
    project: orm.Mapped[DatabaseProject] = orm.relationship(
        back_populates="models"
    )

    tool_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(Tool.id))
    tool: orm.Mapped[Tool] = orm.relationship()

    version_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey(Version.id)
    )
    version: orm.Mapped[Version] = orm.relationship()

    nature_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey(Nature.id)
    )
    nature: orm.Mapped[Nature] = orm.relationship()

    editing_mode: orm.Mapped[EditingMode | None]

    t4c_models: orm.Mapped[list[DatabaseT4CModel]] = orm.relationship(
        back_populates="model"
    )
    git_models: orm.Mapped[list[DatabaseGitModel]] = orm.relationship(
        back_populates="model"
    )

    restrictions: orm.Mapped[DatabaseToolModelRestrictions] = orm.relationship(
        back_populates="model", uselist=False
    )


class CapellaModel(pydantic.BaseModel):
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
