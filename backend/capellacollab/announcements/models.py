# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic


class AnnouncementLevel(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"
    ALERT = "alert"


class CreateAnnouncementRequest(core_pydantic.BaseModel):
    level: AnnouncementLevel
    title: str
    message: str
    dismissible: bool


class AnnouncementResponse(CreateAnnouncementRequest):
    id: int


class DatabaseAnnouncement(database.Base):
    __tablename__ = "announcements"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )
    title: orm.Mapped[str]
    message: orm.Mapped[str]
    level: orm.Mapped[AnnouncementLevel]
    dismissible: orm.Mapped[bool] = orm.mapped_column(default=False)
