# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.announcements import crud, models
from capellacollab.core import database

from . import exceptions


def get_existing_announcement(
    announcement_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseAnnouncement:
    if announcement := crud.get_announcement_by_id(db, announcement_id):
        return announcement

    raise exceptions.AnnouncementNotFoundError(announcement_id)
