# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.users import models


def get_user_by_name(
    db: orm.Session, username: str
) -> models.DatabaseUser | None:
    return db.execute(
        sa.select(models.DatabaseUser).where(
            models.DatabaseUser.name == username
        )
    ).scalar_one_or_none()


def get_user_by_id(
    db: orm.Session, user_id: int
) -> models.DatabaseUser | None:
    return db.execute(
        sa.select(models.DatabaseUser).where(models.DatabaseUser.id == user_id)
    ).scalar_one_or_none()


def get_users(db: orm.Session) -> abc.Sequence[models.DatabaseUser]:
    return db.execute(sa.select(models.DatabaseUser)).scalars().all()


def get_admin_users(db: orm.Session) -> abc.Sequence[models.DatabaseUser]:
    return (
        db.execute(
            sa.select(models.DatabaseUser).where(
                models.DatabaseUser.role == models.Role.ADMIN
            )
        )
        .scalars()
        .all()
    )


def create_user(
    db: orm.Session, username: str, role: models.Role = models.Role.USER
) -> models.DatabaseUser:
    user = models.DatabaseUser(
        name=username,
        role=role,
        created=datetime.datetime.now(datetime.UTC),
        projects=[],
        events=[],
    )
    db.add(user)
    db.commit()

    return user


def update_role_of_user(
    db: orm.Session, user: models.DatabaseUser, role: models.Role
) -> models.DatabaseUser:
    user.role = role
    db.commit()
    return user


def update_last_login(
    db: orm.Session,
    user: models.DatabaseUser,
    last_login: datetime.datetime | None = None,
) -> models.DatabaseUser:
    if not last_login:
        last_login = datetime.datetime.now(datetime.UTC)
    user.last_login = last_login
    db.commit()
    return user


def delete_user(db: orm.Session, user: models.DatabaseUser):
    db.delete(user)
    db.commit()
