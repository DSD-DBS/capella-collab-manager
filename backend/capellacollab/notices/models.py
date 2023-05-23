# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column

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

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str]
    message: Mapped[str]
    level: Mapped[NoticeLevel]
