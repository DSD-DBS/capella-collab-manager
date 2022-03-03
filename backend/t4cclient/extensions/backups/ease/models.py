from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from t4cclient.core.database import Base


class EASEBackupRequest(BaseModel):
    git_model_id: str
    t4c_model_id: str

    class Config:
        orm_mode = True


class EASEBackupResponse(EASEBackupRequest):
    id: int

    class Config:
        orm_mode = True


class DB_EASEBackup(Base):
    __tablename__ = "EASEBackup"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String)
    gitmodel = Column(Integer, ForeignKey("git_models.id"))
    t4cmodel = Column(Integer, ForeignKey("projects.id"))
    project = Column(
        String,
        ForeignKey("repositories.name"),
        primary_key=True,
    )
