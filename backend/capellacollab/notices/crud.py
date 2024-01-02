# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.notices import models


def get_notices(db: orm.Session) -> abc.Sequence[models.DatabaseNotice]:
    return db.execute(sa.select(models.DatabaseNotice)).scalars().all()


def get_notice_by_id(
    db: orm.Session, notice_id: int
) -> models.DatabaseNotice | None:
    return db.execute(
        sa.select(models.DatabaseNotice).where(
            models.DatabaseNotice.id == notice_id
        )
    ).scalar_one_or_none()


def create_notice(
    db: orm.Session, body: models.CreateNoticeRequest
) -> models.DatabaseNotice:
    notice = models.DatabaseNotice(**body.model_dump())
    db.add(notice)
    db.commit()
    return notice


def delete_notice(db: orm.Session, notice: models.DatabaseNotice) -> None:
    db.delete(notice)
    db.commit()
