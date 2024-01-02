# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum

import pydantic


class FileType(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FileTree(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    path: str
    name: str
    type: FileType
    children: list[FileTree] | None = None
