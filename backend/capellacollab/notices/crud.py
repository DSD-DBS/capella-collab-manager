# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy.orm import Session

from capellacollab.notices.models import CreateNoticeRequest, DatabaseNotice


def get_notice_by_id(db: Session, id: int):
    return db.query(DatabaseNotice).filter(DatabaseNotice.id == id).first()


def get_all_notices(db: Session):
    return db.query(DatabaseNotice).all()


def create_notice(db: Session, body: CreateNoticeRequest):
    notice = DatabaseNotice(**body.dict())
    db.add(notice)
    db.commit()
    return notice


def delete_notice(db: Session, notice: DatabaseNotice):
    notice.delete()
    db.commit()
