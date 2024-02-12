# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from pydantic import BaseModel, ConfigDict, Field
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


class CreateNoticeRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: NoticeLevel = Field(
        description="The severity or indication level of a notice",
        examples=["info"],
    )
    title: str = Field(
        description="The title of a notice",
        examples=["Planned Maintenance 13.09.2021"],
    )
    message: str = Field(
        description="The message body of a notice",
        examples=[
            "The site will be unavailable from 7:00 until 14:00 on 13.09.2021."
        ],
    )


class NoticeResponse(CreateNoticeRequest):
    id: int


class DatabaseNotice(database.Base):
    __tablename__ = "notices"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, index=True)
    title: orm.Mapped[str]
    message: orm.Mapped[str]
    level: orm.Mapped[NoticeLevel]
