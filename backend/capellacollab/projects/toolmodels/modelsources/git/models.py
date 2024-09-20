# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseToolModel


class PostGitModel(core_pydantic.BaseModel):
    path: str
    entrypoint: str
    revision: str
    username: str
    password: str


class PutGitModel(PostGitModel):
    primary: bool


class GitModel(PostGitModel):
    id: int
    primary: bool
    repository_id: str | None

    @pydantic.field_serializer("password")
    def transform_password(self, data: str) -> bool:
        return data is not None and len(data) > 0


class DatabaseGitModel(database.Base):
    __tablename__ = "git_models"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )
    path: orm.Mapped[str]
    entrypoint: orm.Mapped[str]
    revision: orm.Mapped[str]
    primary: orm.Mapped[bool]

    model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("models.id"), init=False
    )
    model: orm.Mapped["DatabaseToolModel"] = orm.relationship(
        back_populates="git_models"
    )

    username: orm.Mapped[str]
    password: orm.Mapped[str]

    repository_id: orm.Mapped[str | None] = orm.mapped_column(default=None)

    @classmethod
    def from_post_git_model(
        cls, model: "DatabaseToolModel", primary: bool, new_model: PostGitModel
    ):
        return cls(
            primary=primary,
            model=model,
            **new_model.model_dump(),
        )


class GitModelStatus(enum.Enum):
    ACCESSIBLE = "accessible"
    INACCESSIBLE = "inaccessible"
    UNSET = "unset"


class ModelArtifactStatus(enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    UNCONFIGURED = "unconfigured"
    UNSUPPORTED = "unsupported"
