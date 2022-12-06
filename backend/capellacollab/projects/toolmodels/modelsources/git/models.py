# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

from pydantic import BaseModel, validator
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

from capellacollab.core.database import Base


def validate_path(path: t.Optional[str]):
    if path:
        sequence_blacklist = ["..", "%"]

        for sequence in sequence_blacklist:
            if sequence in path:
                raise ValueError(
                    "The provide path contains invalid sequences."
                )
    return path


class PostGitModel(BaseModel):
    path: str
    entrypoint: str
    revision: str
    username: str
    password: str

    _validate_path = validator("path", allow_reuse=True)(validate_path)


class PatchGitModel(PostGitModel):
    primary: bool


class ResponseGitModel(BaseModel):
    id: int
    name: str
    path: str
    entrypoint: str
    revision: str
    primary: bool
    username: str
    password: bool

    @validator("password", pre=True)
    def transform_password(cls, passw: t.Union[str, bool]) -> bool:
        if isinstance(passw, bool):
            return passw
        return passw is not None and len(passw) > 0

    class Config:
        orm_mode = True


class DatabaseGitModel(Base):
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
    def from_post_git_model(
        cls, model_id: int, primary: bool, new_model: PostGitModel
    ):
        return cls(
            name="",
            primary=primary,
            model_id=model_id,
            **new_model.dict(),
        )
