# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)
from capellacollab.tools import models as tools_models

from .restrictions import models as restrictions_models

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.projects.toolmodels.modelsources.git.models import (
        DatabaseGitModel,
    )
    from capellacollab.projects.toolmodels.modelsources.t4c.models import (
        DatabaseT4CModel,
    )
    from capellacollab.tools.models import (
        DatabaseNature,
        DatabaseTool,
        DatabaseVersion,
    )

    from .restrictions.models import DatabaseToolModelRestrictions


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


class DatabaseCapellaModel(database.Base):
    __tablename__ = "models"
    __table_args__ = (sa.UniqueConstraint("project_id", "slug"),)

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, unique=True
    )

    name: orm.Mapped[str] = orm.mapped_column(index=True)
    slug: orm.Mapped[str]
    description: orm.Mapped[str]

    configuration: orm.Mapped[dict[str, str] | None]

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id")
    )
    project: orm.Mapped[DatabaseProject] = orm.relationship(
        back_populates="models"
    )

    tool_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("tools.id"))
    tool: orm.Mapped[DatabaseTool] = orm.relationship()

    version_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("versions.id")
    )
    version: orm.Mapped[DatabaseVersion] = orm.relationship()

    nature_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("types.id")
    )
    nature: orm.Mapped[DatabaseNature] = orm.relationship()

    editing_mode: orm.Mapped[EditingMode | None]

    t4c_models: orm.Mapped[list[DatabaseT4CModel]] = orm.relationship(
        back_populates="model"
    )
    git_models: orm.Mapped[list[DatabaseGitModel]] = orm.relationship(
        back_populates="model"
    )

    restrictions: orm.Mapped[
        DatabaseToolModelRestrictions | None
    ] = orm.relationship(
        back_populates="model", uselist=False, cascade="delete"
    )


class CapellaModel(pydantic.BaseModel):
    id: int
    slug: str
    name: str
    description: str
    tool: tools_models.ToolBase
    version: tools_models.ToolVersionBase | None
    nature: tools_models.ToolNatureBase | None
    git_models: list[git_models.GitModel] | None
    t4c_models: list[t4c_models.T4CModel] | None

    restrictions: restrictions_models.ToolModelRestrictions | None

    class Config:
        orm_mode = True
