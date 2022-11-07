# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t
from datetime import datetime

from pydantic import BaseModel, validator
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.git.models import (
    DatabaseGitModel,
    ResponseGitModel,
)
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
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
    k8s_cronjob_id: str
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

        return BackupJob(
            id=OPERATOR.get_cronjob_last_run(values["k8s_cronjob_id"]),
            date=OPERATOR.get_cronjob_last_starting_date(
                values["k8s_cronjob_id"]
            ),
            state=OPERATOR.get_cronjob_last_state(values["k8s_cronjob_id"]),
        )

    class Config:
        orm_mode = True


class DatabaseBackup(Base):
    __tablename__ = "backups"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    k8s_cronjob_id = Column(String)
    git_model_id = Column(Integer, ForeignKey("git_models.id"))
    git_model = relationship(
        DatabaseGitModel,
    )
    t4c_model_id = Column(Integer, ForeignKey("t4c_models.id"))
    t4c_model = relationship(
        DatabaseT4CModel,
    )

    created_by = Column(String)
    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship(
        DatabaseCapellaModel,
    )
    t4c_username = Column(String)
    t4c_password = Column(String)

    include_commit_history = Column(Boolean)
    run_nightly = Column(Boolean)
