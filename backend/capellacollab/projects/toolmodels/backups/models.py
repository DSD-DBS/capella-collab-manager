# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t
from datetime import datetime

from pydantic import BaseModel, validator
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import (
    DatabaseGitModel,
    ResponseGitModel,
)
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
    SimpleT4CModel,
)
from capellacollab.sessions.operators import OPERATOR


class CreateBackup(BaseModel):
    git_model_id: int
    t4c_model_id: int
    include_commit_history: bool
    run_nightly: bool

    class Config:
        orm_mode = True


class BackupJob(BaseModel):
    id: t.Union[str, None]
    date: t.Union[datetime, None]
    state: str


class Job(BaseModel):
    include_commit_history: bool


class Backup(BaseModel):
    id: int
    k8s_cronjob_id: t.Optional[str]
    lastrun: t.Optional[BackupJob]
    t4c_model: SimpleT4CModel
    git_model: ResponseGitModel
    run_nightly: bool
    include_commit_history: bool

    @validator("lastrun", pre=True, always=True)
    @classmethod
    def resolve_cronjob(
        cls, value: t.Optional[BackupJob], values
    ) -> BackupJob:
        if isinstance(value, BackupJob):
            return value

        if "k8s_cronjob_id" not in values:
            return None

        label = "app.capellacollab/parent"
        if job_id := OPERATOR.get_cronjob_last_run_by_label(
            label, values["k8s_cronjob_id"]
        ):
            return BackupJob(
                id=job_id,
                date=OPERATOR.get_job_starting_date(job_id),
                state=OPERATOR.get_job_state(job_id),
            )

        return None

    class Config:
        orm_mode = True


class DatabaseBackup(Base):
    __tablename__ = "backups"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    k8s_cronjob_id: str = Column(String)
    git_model_id: int = Column(Integer, ForeignKey("git_models.id"))
    git_model: DatabaseGitModel = relationship(
        DatabaseGitModel,
    )
    t4c_model_id: int = Column(Integer, ForeignKey("t4c_models.id"))
    t4c_model: DatabaseT4CModel = relationship(
        DatabaseT4CModel,
    )

    created_by: str = Column(String)
    model_id: int = Column(Integer, ForeignKey("models.id"))
    model: DatabaseCapellaModel = relationship(
        DatabaseCapellaModel,
    )
    t4c_username: str = Column(String)
    t4c_password: str = Column(String)

    include_commit_history: bool = Column(Boolean, nullable=False)
    run_nightly: bool = Column(Boolean, nullable=False)
