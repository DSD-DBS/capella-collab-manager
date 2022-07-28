# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

# 1st party:
from capellacollab.core.database import Base


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
    username: t.Union[str, None]


class GetRevisionsModel(BaseModel):
    revisions: t.dict[str, t.list[str]]


class GitCredentials(BaseModel):
    username: t.Union[str, None]
    password: t.Union[str, None]


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
    model_id = Column(Integer, ForeignKey("capella_models.id"))
    model = relationship("Model", back_populates="git_model")
    username = Column(String)
    password = Column(String)
