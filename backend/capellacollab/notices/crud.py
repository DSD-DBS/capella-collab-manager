# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.notices import models


def get_notices(db: Session) -> Sequence[models.DatabaseNotice]:
    return db.execute(select(models.DatabaseNotice)).scalars().all()


def get_notice_by_id(
    db: Session, notice_id: int
) -> models.DatabaseNotice | None:
    return db.execute(
        select(models.DatabaseNotice).where(
            models.DatabaseNotice.id == notice_id
        )
    ).scalar_one_or_none()


def create_notice(
    db: Session, body: models.CreateNoticeRequest
) -> models.DatabaseNotice:
    notice = models.DatabaseNotice(**body.dict())
    db.add(notice)
    db.commit()
    return notice


def delete_notice(db: Session, notice: models.DatabaseNotice) -> None:
    db.delete(notice)
    db.commit()
