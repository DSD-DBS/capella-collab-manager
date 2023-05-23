# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.sessions.models import DatabaseSession
from capellacollab.tools.models import Version
from capellacollab.users.models import DatabaseUser


def get_sessions(db: Session) -> Sequence[DatabaseSession]:
    return db.execute(select(DatabaseSession)).scalars().all()


def get_sessions_for_user(
    db: Session, username: str
) -> Sequence[DatabaseSession]:
    return (
        db.execute(
            select(DatabaseSession).where(
                DatabaseSession.owner_name == username
            )
        )
        .scalars()
        .all()
    )


def get_sessions_for_project(
    db: Session, project: DatabaseProject
) -> Sequence[DatabaseSession]:
    return (
        db.execute(
            select(DatabaseSession).where(
                DatabaseSession.project_id == project.id
            )
        )
        .scalars()
        .all()
    )


def get_session_by_id(db: Session, session_id: str) -> DatabaseSession | None:
    return db.execute(
        select(DatabaseSession).where(DatabaseSession.id == session_id)
    ).scalar_one_or_none()


def exist_readonly_session_for_user_project_version(
    db: Session,
    owner: DatabaseUser,
    project: DatabaseProject,
    version: Version,
) -> bool:
    return (
        db.execute(
            select(DatabaseSession)
            .where(DatabaseSession.owner == owner)
            .where(DatabaseSession.project == project)
            .where(DatabaseSession.version == version)
        ).scalar_one_or_none()
        is not None
    )


def count_sessions(db: Session) -> int:
    count = db.scalar(
        select(func.count()).select_from(  # pylint: disable=not-callable
            DatabaseSession
        )
    )
    return count if count else 0


def create_session(db: Session, session: DatabaseSession) -> DatabaseSession:
    if not session.created_at:
        session.created_at = datetime.datetime.now()

    db.add(session)
    db.commit()
    return session


def delete_session(db: Session, session: DatabaseSession) -> None:
    db.delete(session)
    db.commit()
