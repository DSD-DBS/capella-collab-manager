from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from t4cclient.core.database import Base


class EASEBackupRequest(BaseModel):
    gitmodel: int
    t4cmodel: int

    class Config:
        orm_mode = True


class EASEBackupJob(BaseModel):
    id: str | None
    date: datetime | None
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
    t4cmodel = Column(Integer, ForeignKey("projects.id"))
    username = Column(String)
    project = Column(
        String,
        ForeignKey("repositories.name"),
        primary_key=True,
    )
