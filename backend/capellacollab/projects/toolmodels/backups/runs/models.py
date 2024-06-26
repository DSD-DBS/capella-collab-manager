# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

import capellacollab.users.models as users_models
from capellacollab.core import pydantic as core_pydantic
from capellacollab.core.database import Base

from .. import models as pipeline_models


class PipelineRunStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class DatabasePipelineRun(Base):
    __tablename__ = "pipeline_run"
    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    status: orm.Mapped[PipelineRunStatus]

    pipeline_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("backups.id"), init=False
    )
    pipeline: orm.Mapped[pipeline_models.DatabaseBackup] = orm.relationship(
        pipeline_models.DatabaseBackup
    )

    triggerer_id: orm.Mapped[str] = orm.mapped_column(
        sa.ForeignKey("users.id"), init=False
    )
    triggerer: orm.Mapped[users_models.DatabaseUser] = orm.relationship(
        users_models.DatabaseUser
    )

    trigger_time: orm.Mapped[datetime.datetime]

    environment: orm.Mapped[dict[str, str]]

    reference_id: orm.Mapped[str | None] = orm.mapped_column(default=None)
    end_time: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        default=None
    )
    logs_last_fetched_timestamp: orm.Mapped[datetime.datetime | None] = (
        orm.mapped_column(default=None)
    )


class PipelineRun(core_pydantic.BaseModel):
    id: int
    reference_id: str | None = None
    triggerer: users_models.User
    trigger_time: datetime.datetime
    status: PipelineRunStatus
    environment: dict[str, str]

    _validate_trigger_time = pydantic.field_serializer("trigger_time")(
        core_pydantic.datetime_serializer
    )


class BackupPipelineRun(core_pydantic.BaseModel):
    include_commit_history: bool | None = None
