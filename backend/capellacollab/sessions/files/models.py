# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum

from capellacollab.core import pydantic as core_pydantic


class FileType(enum.Enum):
    FILE = "file"
    DIRECTORY = "directory"


class FileTree(core_pydantic.BaseModel):
    path: str
    name: str
    type: FileType
    children: list[FileTree] | None = None
