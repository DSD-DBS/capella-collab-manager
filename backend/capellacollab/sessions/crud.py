# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.sessions.models import DatabaseSession
from capellacollab.tools.models import Version
from capellacollab.users.models import DatabaseUser


def get_sessions_for_user(db: Session, username: str):
    return (
        db.query(DatabaseSession)
        .filter(DatabaseSession.owner_name == username)
        .all()
    )


def get_sessions_for_repository(db: Session, repository: str):
    return (
        db.query(DatabaseSession)
        .filter(DatabaseSession.repository == repository)
        .all()
    )


def get_session_by_id(db: Session, _id: str) -> DatabaseSession | None:
    return db.execute(
        select(DatabaseSession).where(DatabaseSession.id == _id)
    ).scalar()


def get_session_by_user_project_version(
    db: Session,
    owner: DatabaseUser,
    project: DatabaseProject,
    version: Version,
) -> DatabaseSession | None:
    return (
        db.query(DatabaseSession)
        .filter(DatabaseSession.owner == owner)
        .filter(DatabaseSession.project == project)
        .filter(DatabaseSession.version == version)
        .first()
    )


def get_all_sessions(db: Session):
    return db.query(DatabaseSession).all()


def create_session(db: Session, session: DatabaseSession):
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session: DatabaseSession):
    db.delete(session)
    db.commit()
