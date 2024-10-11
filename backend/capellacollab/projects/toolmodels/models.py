# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects import models as projects_models

# Importing the modules here does not work as it produces a pydantic error for the CapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import GitModel
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    SimpleT4CModelWithRepository,
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

    from .provisioning.models import DatabaseModelProvisioning
    from .restrictions.models import DatabaseToolModelRestrictions


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class PostToolModel(core_pydantic.BaseModel):
    name: str
    description: str | None = None
    tool_id: int


class PatchToolModel(core_pydantic.BaseModel):
    name: str | None = None
    description: str | None = None
    version_id: int | None = None
    nature_id: int | None = None
    project_slug: str | None = None
    display_order: int | None = None


class ToolDetails(core_pydantic.BaseModel):
    version_id: int
    nature_id: int


class DatabaseToolModel(database.Base):
    __tablename__ = "models"
    __table_args__ = (sa.UniqueConstraint("project_id", "slug"),)

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, unique=True
    )

    name: orm.Mapped[str] = orm.mapped_column(index=True)
    slug: orm.Mapped[str]
    description: orm.Mapped[str]
    display_order: orm.Mapped[int | None]

    configuration: orm.Mapped[dict[str, str] | None]

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id"), init=False
    )
    project: orm.Mapped[DatabaseProject] = orm.relationship(
        back_populates="models"
    )

    tool_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("tools.id"), init=False
    )
    tool: orm.Mapped[DatabaseTool] = orm.relationship()

    version_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("versions.id"), init=False
    )
    version: orm.Mapped[DatabaseVersion | None] = orm.relationship(
        default=None
    )

    nature_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("types.id"), init=False
    )
    nature: orm.Mapped[DatabaseNature | None] = orm.relationship(default=None)

    editing_mode: orm.Mapped[EditingMode | None] = orm.mapped_column(
        default=None
    )

    t4c_models: orm.Mapped[list[DatabaseT4CModel]] = orm.relationship(
        default_factory=list, back_populates="model"
    )
    git_models: orm.Mapped[list[DatabaseGitModel]] = orm.relationship(
        default_factory=list, back_populates="model"
    )

    restrictions: orm.Mapped[DatabaseToolModelRestrictions | None] = (
        orm.relationship(
            back_populates="model",
            uselist=False,
            cascade="delete",
            default=None,
        )
    )

    provisioning: orm.Mapped[list[DatabaseModelProvisioning]] = (
        orm.relationship(
            back_populates="tool_model",
            cascade="delete",
            default_factory=list,
        )
    )


class ToolModel(core_pydantic.BaseModel):
    id: int
    slug: str
    name: str
    description: str
    display_order: int | None
    tool: tools_models.Tool
    version: tools_models.ToolVersion | None = None
    nature: tools_models.ToolNature | None = None
    git_models: list[GitModel] | None = None
    t4c_models: list[SimpleT4CModelWithRepository] | None = None
    restrictions: restrictions_models.ToolModelRestrictions | None = None


class SimpleToolModel(core_pydantic.BaseModel):
    id: int
    slug: str
    name: str
    project: projects_models.SimpleProject


class SimpleToolModelWithoutProject(core_pydantic.BaseModel):
    id: int
    slug: str
    name: str
    git_models: list[GitModel] | None = None
