# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.toolmodels import models as toolsmodels_models
from capellacollab.tools import models as tools_models

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.tools.models import DatabaseVersion


class ProjectTool(core_pydantic.BaseModel):
    id: int | None

    tool_version: tools_models.SimpleToolVersion
    tool: tools_models.Tool
    used_by: list[toolsmodels_models.SimpleToolModelWithoutProject] = []

    @pydantic.model_validator(mode="before")
    @classmethod
    def derive_tool_from_version(cls, data: t.Any) -> t.Any:
        if not isinstance(data, DatabaseProjectToolAssociation):
            return data

        data_dict = data.__dict__
        data_dict["tool"] = data.tool_version.tool
        return data_dict


class PostProjectToolRequest(core_pydantic.BaseModel):
    tool_id: int
    tool_version_id: int


class DatabaseProjectToolAssociation(database.Base):
    __tablename__ = "project_tool_association"

    id: orm.Mapped[int] = orm.mapped_column(
        sa.Integer,
        init=False,
        primary_key=True,
        autoincrement=True,
    )

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id"), primary_key=True, init=False
    )
    project: orm.Mapped["DatabaseProject"] = orm.relationship(
        back_populates="tools"
    )

    tool_version_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("versions.id"), primary_key=True, init=False
    )
    tool_version: orm.Mapped["DatabaseVersion"] = orm.relationship()
