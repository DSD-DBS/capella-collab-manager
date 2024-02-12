# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import orm

from capellacollab.core import database

# Importing the modules here does not work as it produces a pydantic error for the CapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import GitModel
from capellacollab.projects.toolmodels.modelsources.t4c.models import T4CModel
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


class PostCapellaModel(BaseModel):
    name: str = Field(
        description="The name of a model provided at creation",
        examples=["Coffee Machine"],
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        description="The description of a model provided at creation",
        examples=["A model of a coffee machine."],
        max_length=1500,
    )
    tool_id: int = Field(
        description="The model tool ID for a model provided at creation",
    )


class PatchCapellaModel(BaseModel):
    name: str | None = Field(
        default=None,
        description="An optional new name for a model provided for patching",
        examples=["Espresso Machine"],
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        description="An optional new description for a model provided for patching",
        examples=["A model of an espresso machine."],
        max_length=1500,
    )
    version_id: int | None = Field(
        default=None,
        description="An optional model version ID for a model provided for patching",
    )
    nature_id: int | None = Field(
        default=None,
        description="An optional nature ID for a model provided for patching",
    )
    project_slug: str | None = Field(
        default=None,
        description="An optional project slug for a model for patching, derived from the model name provided by the model update request",
        examples=["espresso-machine"],
    )
    display_order: int | None = Field(
        default=None,
        description="An optional display order index for a model in the Project Overview provided for patching",
    )


class ToolDetails(BaseModel):
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
    display_order: orm.Mapped[int | None]

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

    restrictions: orm.Mapped[DatabaseToolModelRestrictions] = orm.relationship(
        back_populates="model", uselist=False, cascade="delete"
    )


class CapellaModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="The unique ID of a model", examples=[1])
    slug: str = Field(
        description="The unique slug of a model", examples=["coffee-machine"]
    )
    name: str = Field(
        description="The name of a model",
        examples=["Coffee Machine"],
        max_length=255,
    )
    description: str = Field(
        description="The description of a model",
        examples=["A model of a coffee machine."],
        max_length=1500,
    )
    display_order: int | None = Field(
        description="The display order index of a model in the Project Overview",
    )
    tool: tools_models.ToolBase = Field(
        description="The id, name, and tool integrations of a tool"
    )
    version: tools_models.ToolVersionBase | None = Field(
        default=None,
        description="The id, name, and recommended or deprecated states of a tool version",
    )
    nature: tools_models.ToolNatureBase | None = Field(
        default=None, description="The id and name of the model's tool nature"
    )
    git_models: list[GitModel] | None = Field(
        default=None,
        description="A list of git models associated with the model",
    )
    t4c_models: list[T4CModel] | None = Field(
        default=None,
        description="A list of T4C models associated with the model",
    )

    restrictions: restrictions_models.ToolModelRestrictions | None = None
