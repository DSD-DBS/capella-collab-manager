# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t
from numpy import integer

# 3rd party:
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

# 1st party:
from capellacollab.core.database import Base


class GitType(Enum):
    GENERAL = "General"
    GITLAB = "GitLab"
    GITHUB = "GitHub"
    AZUREDEVOPS = "AzureDevOps"


class GitSettings(BaseModel):
    type: GitType
    name: str
    url: str


class GitSettingsGitGetResponse(BaseModel):
    id: int
    name: str
    url: str
    type: GitType


class DB_GitSettings(Base):
    __tablename__ = "git_settings"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    url = Column(String)
    type = Column(String)
