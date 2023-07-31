# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import hashlib

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import credentials

from . import models


def create_token(
    db: orm.Session, user_id: int, description: str
) -> tuple[models.DatabaseUserTokenModel, str]:
    password = credentials.generate_password(32)
    token_data = models.DatabaseUserTokenModel(
        user_id=user_id,
        hash=hashlib.sha512(bytes(password, "utf-8")).hexdigest(),
        expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        description=description,
    )
    db.add(token_data)
    db.commit()
    return token_data, password


def get_token(
    db: orm.Session, token: str
) -> models.DatabaseUserTokenModel | None:
    return db.execute(
        sa.select(models.DatabaseUserTokenModel).where(
            models.DatabaseUserTokenModel.hash
            == hashlib.sha512(bytes(token, "utf-8")).hexdigest()
        )
    ).scalar_one_or_none()


def get_token_by_user(
    db: orm.Session, user_id: int
) -> models.DatabaseUserTokenModel | None:
    return db.execute(
        sa.select(models.DatabaseUserTokenModel).where(
            models.DatabaseUserTokenModel.user_id == user_id
        )
    ).scalar_one_or_none()


def delete_token(
    db: orm.Session, existing_token: models.DatabaseUserTokenModel
) -> models.DatabaseUserTokenModel:
    db.delete(existing_token)
    return existing_token
