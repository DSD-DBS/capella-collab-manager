# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from pydantic import BaseModel


class NoticeLevel(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    ALERT = "alert"


class CreateNoticeRequest(BaseModel):
    level: NoticeLevel
    title: str
    message: str
    scope: str

    class Config:
        orm_mode = True


class NoticeResponse(CreateNoticeRequest):
    id: int
