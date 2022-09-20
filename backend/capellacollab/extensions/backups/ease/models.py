# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String

from capellacollab.core.database import Base


class EASEBackupRequest(BaseModel):
    gitmodel: int
    t4cmodel: int

    class Config:
        orm_mode = True


class EASEBackupJob(BaseModel):
    id: t.Union[str, None]
    date: t.Union[datetime, None]
    state: str


class EASEBackupResponse(EASEBackupRequest):
    id: int
    lastrun: EASEBackupJob

    class Config:
        orm_mode = True


class DB_EASEBackup(Base):
    __tablename__ = "EASEBackup"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reference = Column(String)
    gitmodel = Column(Integer, ForeignKey("git_models.id"))
    t4cmodel = Column(Integer, ForeignKey("t4c_models.id"))
    username = Column(String)
    project = Column(
        String,
        ForeignKey("projects.name"),
        primary_key=True,
    )
