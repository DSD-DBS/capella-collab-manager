# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseToolModel
    from capellacollab.projects.toolmodels.modelsources.git.models import (
        DatabaseGitModel,
    )
    from capellacollab.projects.toolmodels.modelsources.t4c.models import (
        DatabaseT4CModel,
    )

    from .runs import models as runs_models


class CreatePipeline(core_pydantic.BaseModel):
    git_model_id: int
    t4c_model_id: int
    run_nightly: bool


class UpdatePipeline(core_pydantic.BaseModel):
    run_nightly: bool


class Pipeline(core_pydantic.BaseModel):
    id: int

    t4c_model: t4c_models.SimpleT4CModelWithRepository
    git_model: git_models.GitModel
    run_nightly: bool
    next_run: datetime.datetime | None = None

    _validate_next_run = pydantic.field_serializer("next_run")(
        core_pydantic.datetime_serializer_optional
    )


class ExtendedPipeline(Pipeline):
    model: toolmodels_models.SimpleToolModel


ExtendedPipeline.model_rebuild()


class DatabasePipeline(database.Base):
    __tablename__ = "backups"
    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    created_by: orm.Mapped[str]

    t4c_username: orm.Mapped[str]
    t4c_password: orm.Mapped[str]

    run_nightly: orm.Mapped[bool]

    git_model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("git_models.id"), init=False
    )
    git_model: orm.Mapped["DatabaseGitModel"] = orm.relationship()

    t4c_model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("t4c_models.id"), init=False
    )
    t4c_model: orm.Mapped["DatabaseT4CModel"] = orm.relationship()

    model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("models.id"), init=False
    )
    model: orm.Mapped["DatabaseToolModel"] = orm.relationship()

    runs: orm.Mapped[list["runs_models.DatabasePipelineRun"]] = (
        orm.relationship(
            "DatabasePipelineRun",
            back_populates="pipeline",
            cascade="all, delete-orphan",
            default_factory=list,
        )
    )
