# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.announcements import models


def get_announcements(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseAnnouncement]:
    return db.execute(sa.select(models.DatabaseAnnouncement)).scalars().all()


def get_announcement_by_id(
    db: orm.Session, announcement_id: int
) -> models.DatabaseAnnouncement | None:
    return db.execute(
        sa.select(models.DatabaseAnnouncement).where(
            models.DatabaseAnnouncement.id == announcement_id
        )
    ).scalar_one_or_none()


def create_announcement(
    db: orm.Session, body: models.CreateAnnouncementRequest
) -> models.DatabaseAnnouncement:
    announcement = models.DatabaseAnnouncement(**body.model_dump())
    db.add(announcement)
    db.commit()
    return announcement


def update_announcement(
    db: orm.Session,
    announcement: models.DatabaseAnnouncement,
    body: models.CreateAnnouncementRequest,
) -> models.DatabaseAnnouncement:
    for field, value in body.model_dump().items():
        setattr(announcement, field, value)
    db.commit()
    return announcement


def delete_announcement(
    db: orm.Session, announcement: models.DatabaseAnnouncement
) -> None:
    db.delete(announcement)
    db.commit()
