# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import argon2
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import credentials

from . import models


def create_token(
    db: orm.Session,
    user_id: int,
    description: str,
    expiration_date: datetime.date | None,
    source: str | None,
) -> tuple[models.DatabaseUserToken, str]:
    password = "collabmanager_" + credentials.generate_password(32)
    ph = argon2.PasswordHasher()
    if not expiration_date:
        expiration_date = datetime.date.today() + datetime.timedelta(days=30)
    db_token = models.DatabaseUserToken(
        user_id=user_id,
        hash=ph.hash(password),
        expiration_date=expiration_date,
        description=description,
        source=source,
    )
    db.add(db_token)
    db.commit()
    return db_token, password


def get_token_by_token_and_user(
    db: orm.Session, password: str, user_id: int
) -> models.DatabaseUserToken | None:
    ph = argon2.PasswordHasher()

    for token in get_token_by_user(db, user_id):
        try:
            ph.verify(token.hash, password)
            return token
        except argon2.exceptions.VerifyMismatchError:
            pass
    return None


def get_token_by_user(
    db: orm.Session, user_id: int
) -> abc.Sequence[models.DatabaseUserToken]:
    return (
        db.execute(
            sa.select(models.DatabaseUserToken).where(
                models.DatabaseUserToken.user_id == user_id
            )
        )
        .scalars()
        .all()
    )


def get_token_by_user_and_id(
    db: orm.Session, user_id: int, token_id: int
) -> models.DatabaseUserToken | None:
    return db.execute(
        sa.select(models.DatabaseUserToken)
        .where(models.DatabaseUserToken.user_id == user_id)
        .where(models.DatabaseUserToken.id == token_id)
    ).scalar_one_or_none()


def delete_token(
    db: orm.Session, existing_token: models.DatabaseUserToken
) -> None:
    db.delete(existing_token)
    db.commit()
