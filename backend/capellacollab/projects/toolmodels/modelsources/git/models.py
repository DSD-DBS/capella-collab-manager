# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel


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
    def transform_password(cls, passw: str | bool) -> bool:
        if isinstance(passw, bool):
            return passw
        return passw is not None and len(passw) > 0

    class Config:
        orm_mode = True


class DatabaseGitModel(database.Base):
    __tablename__ = "git_models"

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, autoincrement=True
    )
    name: orm.Mapped[str]
    path: orm.Mapped[str]
    entrypoint: orm.Mapped[str]
    revision: orm.Mapped[str]
    primary: orm.Mapped[bool]

    model_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("models.id"))
    model: orm.Mapped["DatabaseCapellaModel"] = orm.relationship(
        back_populates="git_models"
    )

    username: orm.Mapped[str]
    password: orm.Mapped[str]

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
