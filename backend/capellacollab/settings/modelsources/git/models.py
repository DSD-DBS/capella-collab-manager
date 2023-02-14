# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import enum

from pydantic import BaseModel
from sqlalchemy import Column, Enum, Integer, String

from capellacollab.core.database import Base


class GitType(enum.Enum):
    GENERAL = "General"
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    AZUREDEVOPS = "AzureDevOps"


class PostGitInstance(BaseModel):
    type: GitType
    name: str
    url: str
    api_url: str | None

    class Config:
        orm_mode = True


class GitInstance(PostGitInstance):
    id: int


class DatabaseGitInstance(Base):
    __tablename__ = "git_instances"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String)
    url: str = Column(String)
    api_url: str = Column(String)
    type: GitType = Column(Enum(GitType))


class GetRevisionsResponseModel(BaseModel):
    branches: list[str]
    tags: list[str]
    default: str | None


class GitCredentials(BaseModel):
    username: str
    password: str


class GetRevisionModel(BaseModel):
    url: str
    credentials: GitCredentials
