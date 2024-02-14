# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum

import pydantic
from sqlalchemy import orm

from capellacollab.core import database


class NoticeLevel(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    ALERT = "alert"


class CreateNoticeRequest(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    level: NoticeLevel
    title: str
    message: str


class NoticeResponse(CreateNoticeRequest):
    id: int


class DatabaseNotice(database.Base):
    __tablename__ = "notices"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )
    title: orm.Mapped[str]
    message: orm.Mapped[str]
    level: orm.Mapped[NoticeLevel]
