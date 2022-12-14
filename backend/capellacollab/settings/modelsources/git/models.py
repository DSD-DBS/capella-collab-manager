# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import enum
import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, Enum, Integer, String

from capellacollab.core.database import Base


class GitType(enum.Enum):
    GENERAL = "General"
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    AZUREDEVOPS = "AzureDevOps"


class GitSettings(BaseModel):
    type: t.Optional[GitType]
    name: t.Optional[str]
    url: t.Optional[str]


class GitSettingsGitGetResponse(BaseModel):
    id: int
    name: str
    url: str
    type: GitType

    class Config:
        orm_mode = True


class DatabaseGitInstance(Base):
    __tablename__ = "git_settings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    url = Column(String)
    type = Column(Enum(GitType))


class GetRevisionsResponseModel(BaseModel):
    branches: t.List[str]
    tags: t.List[str]
    default: t.Optional[str]


class GitCredentials(BaseModel):
    username: str
    password: str


class GetRevisionModel(BaseModel):
    url: str
    credentials: GitCredentials
