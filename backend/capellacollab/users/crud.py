# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.users import models


def get_user_by_name(db: Session, username: str) -> models.DatabaseUser | None:
    return db.execute(
        select(models.DatabaseUser).where(models.DatabaseUser.name == username)
    ).scalar_one_or_none()


def get_user_by_id(db: Session, user_id: int) -> models.DatabaseUser | None:
    return db.execute(
        select(models.DatabaseUser).where(models.DatabaseUser.id == user_id)
    ).scalar_one_or_none()


def get_users(db: Session) -> Sequence[models.DatabaseUser]:
    return db.execute(select(models.DatabaseUser)).scalars().all()


def create_user(
    db: Session, username: str, role: models.Role = models.Role.USER
) -> models.DatabaseUser:
    user = models.DatabaseUser(
        name=username,
        role=role,
        created=datetime.datetime.now(),
        projects=[],
        events=[],
    )
    db.add(user)
    db.commit()

    return user


def update_role_of_user(
    db: Session, user: models.DatabaseUser, role: models.Role
) -> models.DatabaseUser:
    user.role = role
    db.commit()
    return user


def update_last_login(
    db: Session,
    user: models.DatabaseUser,
    last_login: datetime.datetime | None = None,
) -> models.DatabaseUser:
    if not last_login:
        last_login = datetime.datetime.now()
    user.last_login = last_login
    db.commit()
    return user


def delete_user(db: Session, user: models.DatabaseUser):
    db.delete(user)
    db.commit()
