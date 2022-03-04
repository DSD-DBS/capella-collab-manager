import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from t4cclient.core.database import Base


class RepositoryGitInnerModel(BaseModel):
    path: str
    entrypoint: str
    revision: str

    class Config:
        orm_mode = True


class RepositoryGitModel(BaseModel):
    name: str
    model: RepositoryGitInnerModel

    class Config:
        orm_mode = True


class PatchRepositoryGitModel(BaseModel):
    primary: t.Optional[bool]


class GetRepositoryGitModel(RepositoryGitModel):
    id: int
    primary: bool
    username: str | None


class GitCredentials(BaseModel):
    username: str | None
    password: str | None


class PostGitModel(RepositoryGitModel):
    credentials: GitCredentials


class DB_GitModel(Base):
    __tablename__ = "git_models"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    path = Column(String)
    entrypoint = Column(String)
    revision = Column(String)
    primary = Column(Boolean)
    repository_name = Column(
        String, ForeignKey("repositories.name", ondelete="CASCADE")
    )
    repository = relationship("DatabaseRepository", back_populates="git_models")
    username = Column(String)
    password = Column(String)
