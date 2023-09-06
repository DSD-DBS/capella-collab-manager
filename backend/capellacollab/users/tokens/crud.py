# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import argon2
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import credentials

from . import models


def create_token(
    db: orm.Session, user_id: int, description: str
) -> tuple[models.DatabaseUserTokenModel, str]:
    password = credentials.generate_password(32)
    ph = argon2.PasswordHasher()
    token_data = models.DatabaseUserTokenModel(
        user_id=user_id,
        hash=ph.hash(password),
        expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        description=description,
    )
    db.add(token_data)
    db.commit()
    return token_data, password


def get_token(
    db: orm.Session, password: str, user_id: int
) -> models.DatabaseUserTokenModel | None:
    ph = argon2.PasswordHasher()
    token_list = get_token_by_user(db, user_id)
    if token_list:
        for token in token_list:
            try:
                ph.verify(token.hash, password)
                return token
            except argon2.exceptions.VerifyMismatchError:
                pass
    return None


def get_token_by_user(
    db: orm.Session, user_id: int
) -> abc.Sequence[models.DatabaseUserTokenModel] | None:
    return (
        db.execute(
            sa.select(models.DatabaseUserTokenModel).where(
                models.DatabaseUserTokenModel.user_id == user_id
            )
        )
        .scalars()
        .all()
    )


def delete_token(
    db: orm.Session, existing_token: models.DatabaseUserTokenModel
) -> models.DatabaseUserTokenModel:
    db.delete(existing_token)
    db.commit()
