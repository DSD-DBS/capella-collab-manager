# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables

from . import crud, exceptions, models


def get_own_user(
    db: orm.Session = fastapi.Depends(database.get_db),
    username=fastapi.Depends(auth_injectables.get_username),
) -> models.DatabaseUser:
    if user := crud.get_user_by_name(db, username):
        return user

    raise exceptions.UserNotFoundError(username=username)


def get_existing_user(
    user_id: int | t.Literal["current"],
    db=fastapi.Depends(database.get_db),
    username=fastapi.Depends(auth_injectables.get_username),
) -> models.DatabaseUser:
    if user_id == "current":
        return get_own_user(db, username)

    if user := crud.get_user_by_id(db, user_id):
        return user

    raise exceptions.UserNotFoundError(user_id=user_id)
