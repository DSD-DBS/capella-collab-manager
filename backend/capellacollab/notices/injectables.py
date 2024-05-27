# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.notices import crud, models

from . import exceptions


def get_existing_notice(
    notice_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseNotice:
    if notice := crud.get_notice_by_id(db, notice_id):
        return notice

    raise exceptions.AnnouncementNotFoundError(notice_id)
