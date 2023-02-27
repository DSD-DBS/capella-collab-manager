# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import orm

import capellacollab.users.models as users_models
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
    reference_id: orm.Mapped[str]

    status = orm.Mapped[PipelineRunStatus]

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
    logs_last_fetched_timestamp: orm.Mapped[datetime.datetime]


class PipelineRun(BaseModel):
    id: int
    reference_id: str | None
    triggerer: users_models.User
    trigger_time: datetime.datetime
    status: PipelineRunStatus

    class Config:
        orm_mode = True
