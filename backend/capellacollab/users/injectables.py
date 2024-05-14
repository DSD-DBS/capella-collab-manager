# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables

from . import crud, exceptions, models


def get_own_user(
    db: orm.Session = fastapi.Depends(database.get_db),
    username: str = fastapi.Depends(auth_injectables.get_username),
) -> models.DatabaseUser:
    if user := crud.get_user_by_name(db, username):
        return user

    raise exceptions.UserNotFoundError(username=username)


def get_existing_user(
    user_id: int,
    db=fastapi.Depends(database.get_db),
) -> models.DatabaseUser:
    if user := crud.get_user_by_id(db, user_id):
        return user

    raise exceptions.UserNotFoundError(user_id=user_id)
