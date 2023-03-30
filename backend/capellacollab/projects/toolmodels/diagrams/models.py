# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import datetime

import pydantic


class DiagramMetadata(pydantic.BaseModel):
    name: str
    uuid: str
    success: bool

    class Config:
        orm_mode = True


class DiagramCacheMetadata(pydantic.BaseModel):
    diagrams: list[DiagramMetadata]
    last_updated: datetime.datetime

    class Config:
        orm_mode = True
