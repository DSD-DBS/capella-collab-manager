# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from pydantic import BaseModel
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Enum, Integer, String

from capellacollab.core.database import Base


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

    class Config:
        orm_mode = True


class NoticeResponse(CreateNoticeRequest):
    id: int


class DatabaseNotice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(String)
    level = Column(Enum(NoticeLevel))
