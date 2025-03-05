# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import argon2
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import credentials
from capellacollab.permissions import models as permissions_models
from capellacollab.users import models as users_models

from . import models


def create_token(
    db: orm.Session,
    user: users_models.DatabaseUser,
    scope: permissions_models.GlobalScopes,
    title: str,
    description: str,
    expiration_date: datetime.date | None,
    source: str,
    legacy: bool = False,
    managed: bool = False,
) -> tuple[models.DatabaseUserToken, str]:
    password = credentials.generate_password(32)
    ph = argon2.PasswordHasher(time_cost=1, memory_cost=2048, parallelism=1)
    if not expiration_date:
        expiration_date = datetime.datetime.now(
            tz=datetime.UTC
        ).date() + datetime.timedelta(days=30)
    db_token = models.DatabaseUserToken(
        user=user,
        title=title,
        hash=ph.hash(f"collabmanager_{password}" if legacy else password),
        created_at=datetime.datetime.now(datetime.UTC),
        expiration_date=expiration_date,
        description=description,
        source=source,
        scope=scope,
        managed=managed,
    )
    db.add(db_token)
    db.commit()

    if legacy:
        return db_token, f"collabmanager_{password}"
    return db_token, f"collabmanager_{password}_{db_token.id}"


def get_all_tokens_for_user(
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


def get_token_by_id_and_user(
    db: orm.Session,
    token_id: int,
    user: users_models.DatabaseUser,
) -> models.DatabaseUserToken | None:
    return (
        db.execute(
            sa.select(models.DatabaseUserToken)
            .where(models.DatabaseUserToken.user == user)
            .where(models.DatabaseUserToken.id == token_id)
        )
        .scalars()
        .one_or_none()
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
