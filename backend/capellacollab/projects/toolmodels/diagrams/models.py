# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DiagramMetadata(BaseModel):
    name: str
    uuid: str
    success: str

    class Config:
        orm_mode = True


class DiagramCacheMetadata(BaseModel):
    diagrams: list[DiagramMetadata]
    last_updated: datetime

    class Config:
        orm_mode = True
