# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.sql.schema import ForeignKey

from capellacollab.core import database

if t.TYPE_CHECKING:
    import capellacollab.projects.toolmodels.models as toolmodels_models


class PostGitModel(pydantic.BaseModel):
    path: str
    entrypoint: str
    revision: str
    username: str
    password: str


class PatchGitModel(PostGitModel):
    primary: bool


class GitModel(pydantic.BaseModel):
    id: int
    name: str
    path: str
    entrypoint: str
    revision: str
    primary: bool
    username: str
    password: bool

    @pydantic.validator("password", pre=True)
    @classmethod
    def transform_password(cls, passw: t.Union[str, bool]) -> bool:
        if isinstance(passw, bool):
            return passw
        return passw is not None and len(passw) > 0

    class Config:
        orm_mode = True


class DatabaseGitModel(database.Base):
    __tablename__ = "git_models"
    id: int = sa.Column(
        sa.Integer, primary_key=True, index=True, autoincrement=True
    )
    name: str = sa.Column(sa.String)
    path: str = sa.Column(sa.String)
    entrypoint: str = sa.Column(sa.String)
    revision: str = sa.Column(sa.String)
    primary: bool = sa.Column(sa.Boolean)
    model_id: int = sa.Column(sa.Integer, ForeignKey("models.id"))
    model: "toolmodels_models.DatabaseCapellaModel" = orm.relationship(
        "DatabaseCapellaModel", back_populates="git_models"
    )
    username: str = sa.Column(sa.String)
    password: str = sa.Column(sa.String)

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
