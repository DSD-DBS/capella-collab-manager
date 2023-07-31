# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import hashlib

import sqlalchemy as sa
from sqlalchemy import orm

from . import models


def create_token(
    db: orm.Session, userid: int, token: str, description: str
) -> models.DatabaseUserTokenModel:
    token_data = models.DatabaseUserTokenModel(
        user_id=userid,
        hash=hashlib.sha256(bytes(token, "utf-8")).hexdigest(),
        expiration_date=datetime.datetime.now() + datetime.timedelta(days=30),
        description=description,
    )
    db.add(token_data)
    db.commit()
    return token_data


def get_token(
    db: orm.Session, token: str
) -> models.DatabaseUserTokenModel | None:
    return db.execute(
        sa.select(models.DatabaseUserTokenModel).where(
            models.DatabaseUserTokenModel.hash
            == hashlib.sha256(bytes(token, "utf-8")).hexdigest()
        )
    ).scalar_one_or_none()
