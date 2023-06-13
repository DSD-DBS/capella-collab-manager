# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import helper as auth_helper
from capellacollab.core.authentication import jwt_bearer

from . import crud, models


def get_own_user(
    db: orm.Session = fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
) -> models.DatabaseUser:
    username = auth_helper.get_username(token)

    if user := crud.get_user_by_name(db, username):
        return user

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"reason": f"User {username} was not found"},
    )


def get_existing_user(
    user_id: int | t.Literal["current"],
    db=fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
) -> models.DatabaseUser:
    if user_id == "current":
        return get_own_user(db, token)

    if user := crud.get_user_by_id(db, user_id):
        return user

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"reason": f"User with id {user_id} was not found"},
    )
