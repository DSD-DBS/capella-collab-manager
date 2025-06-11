# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

import capellacollab.users.models as users_models
from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

from .. import models as pipeline_models


class PipelineRunStatus(enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class LogType(str, enum.Enum):
    EVENTS = "events"
    LOGS = "logs"


class DatabasePipelineRunLogLine(database.Base):
    __tablename__ = "pipeline_run_logs"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, autoincrement=True
    )
    run_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("pipeline_run.id"), index=True, init=False
    )
    line: orm.Mapped[str] = orm.mapped_column()
    timestamp: orm.Mapped[datetime.datetime] = orm.mapped_column()
    run: orm.Mapped["DatabasePipelineRun"] = orm.relationship(
        back_populates="logs"
    )
    log_type: orm.Mapped[LogType] = orm.mapped_column(default=LogType.LOGS)
    reason: orm.Mapped[str | None] = orm.mapped_column(default=None)


class DatabasePipelineRun(database.Base):
    __tablename__ = "pipeline_run"
    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    pipeline_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("backups.id"), init=False
    )
    pipeline: orm.Mapped[pipeline_models.DatabasePipeline] = orm.relationship(
        pipeline_models.DatabasePipeline
    )

    triggerer_id: orm.Mapped[str | None] = orm.mapped_column(
        sa.ForeignKey("users.id"), init=False
    )
    triggerer: orm.Mapped[users_models.DatabaseUser | None] = orm.relationship(
        users_models.DatabaseUser
    )

    status: orm.Mapped[PipelineRunStatus] = orm.mapped_column(
        default=PipelineRunStatus.PENDING
    )

    trigger_time: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )

    environment: orm.Mapped[dict[str, str]] = orm.mapped_column(
        default_factory=dict
    )

    reference_id: orm.Mapped[str | None] = orm.mapped_column(default=None)
    end_time: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        default=None
    )
    logs_last_fetched_timestamp: orm.Mapped[datetime.datetime | None] = (
        orm.mapped_column(default=None)
    )
    logs_last_timestamp: orm.Mapped[datetime.datetime | None] = (
        orm.mapped_column(default=None)
    )
    events_last_fetched_timestamp: orm.Mapped[datetime.datetime | None] = (
        orm.mapped_column(default=None)
    )
    logs: orm.Mapped[list[DatabasePipelineRunLogLine]] = orm.relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        default_factory=list,
    )


class PipelineRun(core_pydantic.BaseModel):
    id: int
    reference_id: str | None = None
    triggerer: users_models.User | None
    trigger_time: datetime.datetime
    status: PipelineRunStatus
    environment: dict[str, str]

    _validate_trigger_time = pydantic.field_serializer("trigger_time")(
        core_pydantic.datetime_serializer
    )


class PipelineEvent(core_pydantic.BaseModel):
    timestamp: datetime.datetime
    reason: str | None = None
    message: str | None = None

    _validate_timestamp = pydantic.field_serializer("timestamp")(
        core_pydantic.datetime_serializer
    )


class PipelineLogLine(core_pydantic.BaseModel):
    timestamp: datetime.datetime
    text: str

    _validate_timestamp = pydantic.field_serializer("timestamp")(
        core_pydantic.datetime_serializer
    )
