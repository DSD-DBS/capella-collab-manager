# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from pydantic import BaseModel, validator
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

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
    branches: t.List[str]
    tags: t.List[str]


class GitCredentials(BaseModel):
    username: t.Union[str, None]
    password: t.Union[str, None]


class PostGitModel(RepositoryGitModel):
    credentials: GitCredentials


class NewGitSource(BaseModel):
    path: str
    entrypoint: str
    revision: str
    username: str
    password: str


class ResponseGitSource(NewGitSource):
    id: int

    class Config:
        orm_mode = True


class DB_GitModel(Base):
    __tablename__ = "git_models"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    path = Column(String)
    entrypoint = Column(String)
    revision = Column(String)
    primary = Column(Boolean)
    model_id = Column(Integer, ForeignKey("models.id"))
    model = relationship("DatabaseCapellaModel", back_populates="git_models")
    username = Column(String)
    password = Column(String)

    @classmethod
    def from_new_git_source(cls, model_id: int, source: NewGitSource):
        return cls(
            name="",
            path=source.path,
            entrypoint=source.entrypoint,
            revision=source.revision,
            primary=True,
            model_id=model_id,
            username=source.username,
            password=source.password,
        )


class ResponseGitModel(BaseModel):
    id: int
    name: str
    path: str
    entrypoint: str
    revision: str
    primary: bool
    username: str
    password: bool

    @validator("password", pre=True, whole=True)
    def transform_password(cls, test: str) -> bool:
        if type(test) == bool:
            return test
        return test is not None and len(test) > 0

    class Config:
        orm_mode = True
