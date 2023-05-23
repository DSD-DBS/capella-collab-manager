# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from datetime import datetime

from pydantic import BaseModel, validator
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.models import (
    DatabaseGitModel,
    GitModel,
)
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
    SimpleT4CModel,
)
from capellacollab.sessions import operators


class CreateBackup(BaseModel):
    git_model_id: int
    t4c_model_id: int
    include_commit_history: bool
    run_nightly: bool

    class Config:
        orm_mode = True


class BackupJob(BaseModel):
    id: str
    date: datetime | None
    state: str


class Job(BaseModel):
    include_commit_history: bool


class Backup(BaseModel):
    id: int
    k8s_cronjob_id: str | None
    lastrun: BackupJob | None
    t4c_model: SimpleT4CModel
    git_model: GitModel
    run_nightly: bool
    include_commit_history: bool

    @validator("lastrun", pre=True, always=True)
    @classmethod
    def resolve_cronjob(
        cls, value: BackupJob | None, values
    ) -> BackupJob | None:
        if isinstance(value, BackupJob):
            return value

        if "k8s_cronjob_id" not in values:
            return None

        label = "app.capellacollab/parent"
        if job_id := operators.get_operator().get_cronjob_last_run_by_label(
            label, values["k8s_cronjob_id"]
        ):
            return BackupJob(
                id=job_id,
                date=operators.get_operator().get_job_starting_date(job_id),
                state=operators.get_operator().get_job_state(job_id),
            )

        return None

    class Config:
        orm_mode = True


class DatabaseBackup(Base):
    __tablename__ = "backups"
    id: Mapped[int] = mapped_column(
        primary_key=True, index=True, autoincrement=True
    )

    created_by: Mapped[str]
    k8s_cronjob_id: Mapped[str]

    t4c_username: Mapped[str]
    t4c_password: Mapped[str]

    include_commit_history: Mapped[bool]
    run_nightly: Mapped[bool]

    git_model_id: Mapped[int] = mapped_column(ForeignKey("git_models.id"))
    git_model: Mapped[DatabaseGitModel] = relationship()

    t4c_model_id: Mapped[int] = mapped_column(ForeignKey("t4c_models.id"))
    t4c_model: Mapped[DatabaseT4CModel] = relationship()

    model_id: Mapped[int] = mapped_column(ForeignKey("models.id"))
    model: Mapped[DatabaseCapellaModel] = relationship()
