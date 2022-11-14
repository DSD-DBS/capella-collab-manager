# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import (
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.projects.capellamodels.modelsources.git.models import (
    ResponseGitModel,
)
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    ResponseT4CModel,
)
from capellacollab.tools.models import (
    Nature,
    Tool,
    ToolBase,
    ToolNatureBase,
    ToolVersionBase,
    Version,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.capellamodels.modelsources.git.models import (
        DatabaseGitModel,
    )
    from capellacollab.projects.capellamodels.modelsources.t4c.models import (
        DatabaseT4CModel,
    )
    from capellacollab.projects.models import DatabaseProject


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class CapellaModel(BaseModel):
    name: str
    description: t.Optional[str]
    tool_id: int


class ToolDetails(BaseModel):
    version_id: int
    nature_id: int


class DatabaseCapellaModel(Base):
    __tablename__ = "models"
    __table_args__ = (UniqueConstraint("project_id", "slug"),)

    id = Column(Integer, primary_key=True, index=True, unique=True)
    name = Column(String, index=True)
    slug = Column(String, nullable=False)
    description = Column(String)

    project_id = Column(Integer, ForeignKey("projects.id"))
    project: DatabaseProject = relationship(
        "DatabaseProject", back_populates="models"
    )

    tool_id = Column(Integer, ForeignKey(Tool.id))
    tool: Tool = relationship(Tool)

    version_id = Column(Integer, ForeignKey(Version.id))
    version: Version = relationship(Version)

    nature_id = Column(Integer, ForeignKey(Nature.id))
    nature = relationship(Nature)

    editing_mode = Column(Enum(EditingMode))

    t4c_models: list[DatabaseT4CModel] = relationship(
        "DatabaseT4CModel", back_populates="model"
    )
    git_models: list[DatabaseGitModel] = relationship(
        "DatabaseGitModel", back_populates="model"
    )


class ResponseModel(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    tool: ToolBase
    version: t.Optional[ToolVersionBase]
    nature: t.Optional[ToolNatureBase]
    git_models: t.Optional[list[ResponseGitModel]]
    t4c_models: t.Optional[list[ResponseT4CModel]]

    class Config:
        orm_mode = True
