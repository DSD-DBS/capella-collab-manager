# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

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

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
    from capellacollab.projects.toolmodels.modelsources.git.models import (
        DatabaseGitModel,
    )
    from capellacollab.projects.toolmodels.modelsources.t4c.models import (
        DatabaseT4CModel,
    )

    from .runs import models as runs_models


class CreateBackup(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    git_model_id: int
    t4c_model_id: int
    include_commit_history: bool
    run_nightly: bool


class Backup(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    k8s_cronjob_id: str | None = None

    t4c_model: t4c_models.SimpleT4CModel
    git_model: git_models.GitModel
    run_nightly: bool
    include_commit_history: bool


class DatabaseBackup(database.Base):
    __tablename__ = "backups"
    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, autoincrement=True
    )

    created_by: orm.Mapped[str]
    k8s_cronjob_id: orm.Mapped[str]

    t4c_username: orm.Mapped[str]
    t4c_password: orm.Mapped[str]

    run_nightly: orm.Mapped[bool]
    content: orm.Mapped[dict[str, t.Any]]

    model_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("models.id"))
    model: orm.Mapped["DatabaseCapellaModel"] = orm.relationship()

    runs: orm.Mapped[
        list["runs_models.DatabasePipelineRun"]
    ] = orm.relationship(
        "DatabasePipelineRun",
        back_populates="pipeline",
        cascade="all, delete-orphan",
    )
