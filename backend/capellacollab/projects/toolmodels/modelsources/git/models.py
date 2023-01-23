# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from pydantic import BaseModel, validator
from sqlalchemy import Column, Integer, String, orm
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    import capellacollab.projects.toolmodels.models as toolmodels_models


class PostGitModel(BaseModel):
    path: str
    entrypoint: str
    revision: str
    username: str
    password: str


class PatchGitModel(PostGitModel):
    primary: bool


class GitModel(BaseModel):
    id: int
    name: str
    path: str
    entrypoint: str
    revision: str
    primary: bool
    username: str
    password: bool

    @validator("password", pre=True)
    @classmethod
    def transform_password(cls, passw: t.Union[str, bool]) -> bool:
        if isinstance(passw, bool):
            return passw
        return passw is not None and len(passw) > 0

    class Config:
        orm_mode = True


class DatabaseGitModel(Base):
    __tablename__ = "git_models"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String)
    path: str = Column(String)
    entrypoint: str = Column(String)
    revision: str = Column(String)
    primary: bool = Column(Boolean)
    model_id: int = Column(Integer, ForeignKey("models.id"))
    model: "toolmodels_models.DatabaseCapellaModel" = orm.relationship(
        "DatabaseCapellaModel", back_populates="git_models"
    )
    username: str = Column(String)
    password: str = Column(String)

    @classmethod
    def from_post_git_model(
        cls, model_id: int, primary: bool, new_model: PostGitModel
    ):
        return cls(
            name="",
            primary=primary,
            model_id=model_id,
            **new_model.dict(),
        )
