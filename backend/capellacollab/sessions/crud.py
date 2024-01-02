# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models

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


def get_sessions_for_project(
    db: orm.Session, project: projects_models.DatabaseProject
) -> abc.Sequence[models.DatabaseSession]:
    return (
        db.execute(
            sa.select(models.DatabaseSession).where(
                models.DatabaseSession.project_id == project.id
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


def exist_readonly_session_for_user_project_version(
    db: orm.Session,
    owner: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    version: tools_models.DatabaseVersion,
) -> bool:
    return (
        db.execute(
            sa.select(models.DatabaseSession)
            .where(models.DatabaseSession.owner == owner)
            .where(models.DatabaseSession.project == project)
            .where(models.DatabaseSession.version == version)
        ).scalar_one_or_none()
        is not None
    )


def count_sessions(db: orm.Session) -> int:
    count = db.scalar(
        sa.select(sa.func.count()).select_from(  # pylint: disable=not-callable
            models.DatabaseSession
        )
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
