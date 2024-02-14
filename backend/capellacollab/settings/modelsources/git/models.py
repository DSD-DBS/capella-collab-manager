# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import enum

import pydantic
from sqlalchemy import orm

from capellacollab.core import database


class GitType(enum.Enum):
    GENERAL = "General"
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    AZUREDEVOPS = "AzureDevOps"


class PostGitInstance(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    type: GitType
    name: str
    url: str
    api_url: str | None = None


class GitInstance(PostGitInstance):
    id: int


class DatabaseGitInstance(database.Base):
    __tablename__ = "git_instances"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    name: orm.Mapped[str]
    url: orm.Mapped[str]
    api_url: orm.Mapped[str | None]
    type: orm.Mapped[GitType]


class GetRevisionsResponseModel(pydantic.BaseModel):
    branches: list[str]
    tags: list[str]
    default: str | None = None


class GitCredentials(pydantic.BaseModel):
    username: str
    password: str


class GetRevisionModel(pydantic.BaseModel):
    url: str
    credentials: GitCredentials
