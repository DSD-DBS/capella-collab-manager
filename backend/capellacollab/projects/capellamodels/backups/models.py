# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String

from capellacollab.core.database import Base


class CreateBackup(BaseModel):
    gitmodel: int
    t4cmodel: int
    include_commit_history: bool
    run_nightly: bool

    class Config:
        orm_mode = True


class BackupJob(BaseModel):
    id: t.Union[str, None]
    date: t.Union[datetime, None]
    state: str


class Backup(CreateBackup):
    id: int
    lastrun: BackupJob

    class Config:
        orm_mode = True


class DatabaseBackup(Base):
    __tablename__ = "EASEBackup"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reference = Column(String)
    gitmodel = Column(Integer, ForeignKey("git_models.id"))
    t4cmodel = Column(Integer, ForeignKey("t4c_models.id"))
    username = Column(String)
    model_id = Column(Integer, ForeignKey("models.id"))
    t4c_username = Column(String)
