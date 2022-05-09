# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel


class EditingMode(enum.Enum):
    T4C = "t4c"
    GIT = "git"


class ProjectType(enum.Enum):
    PROJECT = "project"
    LIBRARY = "library"


class Warning(enum.Enum):
    LICENCE_LIMIT = "LICENCE_LIMIT"
    NO_GIT_MODEL_DEFINED = "NO_GIT_MODEL_DEFINED"


class GetProject(BaseModel):
    name: str
    description: str
    editing_mode: EditingMode
    type: ProjectType

    class Config:
        orm_mode = True


class PostRepositoryRequest(BaseModel):
    name: str
