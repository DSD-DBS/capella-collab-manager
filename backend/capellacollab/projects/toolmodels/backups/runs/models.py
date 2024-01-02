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
        primary_key=True, index=True, autoincrement=True
    )
    reference_id: orm.Mapped[str | None]

    status: orm.Mapped[PipelineRunStatus]

    pipeline_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("backups.id")
    )
    pipeline: orm.Mapped[pipeline_models.DatabaseBackup] = orm.relationship(
        pipeline_models.DatabaseBackup
    )

    triggerer_id: orm.Mapped[str] = orm.mapped_column(
        sa.ForeignKey("users.id")
    )
    triggerer: orm.Mapped[users_models.DatabaseUser] = orm.relationship(
        users_models.DatabaseUser
    )

    trigger_time: orm.Mapped[datetime.datetime]
    end_time: orm.Mapped[datetime.datetime | None]
    logs_last_fetched_timestamp: orm.Mapped[datetime.datetime | None]

    environment: orm.Mapped[dict[str, str]]


class PipelineRun(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    reference_id: str | None = None
    triggerer: users_models.User
    trigger_time: datetime.datetime
    status: PipelineRunStatus
    environment: dict[str, str]

    _validate_trigger_time = pydantic.field_serializer("trigger_time")(
        core_pydantic.datetime_serializer
    )


class BackupPipelineRun(pydantic.BaseModel):
    include_commit_history: bool | None = None
