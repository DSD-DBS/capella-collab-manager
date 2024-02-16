# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from . import models


def get_sessions(db: orm.Session) -> abc.Sequence[models.DatabaseSession]:
    return db.execute(sa.select(models.DatabaseSession)).scalars().all()


def get_sessions_for_user(
    db: orm.Session, username: str
) -> abc.Sequence[models.DatabaseSession]:
    return (
        db.execute(
            sa.select(models.DatabaseSession).where(
                models.DatabaseSession.owner_name == username
            )
        )
        .scalars()
        .all()
    )


def get_session_by_id(
    db: orm.Session, session_id: str
) -> models.DatabaseSession | None:
    return db.execute(
        sa.select(models.DatabaseSession).where(
            models.DatabaseSession.id == session_id
        )
    ).scalar_one_or_none()


def count_sessions(db: orm.Session) -> int:
    count = db.scalar(
        sa.select(sa.func.count()).select_from(models.DatabaseSession)
    )
    return count if count else 0


def create_session(
    db: orm.Session, session: models.DatabaseSession
) -> models.DatabaseSession:
    if not session.created_at:
        session.created_at = datetime.datetime.now(datetime.UTC)

    db.add(session)
    db.commit()
    return session


def delete_session(db: orm.Session, session: models.DatabaseSession) -> None:
    db.delete(session)
    db.commit()


def update_session_config(
    db: orm.Session, session: models.DatabaseSession, config: dict[str, str]
) -> models.DatabaseSession:
    session.config = config
    db.commit()
    return session
