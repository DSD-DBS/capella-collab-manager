# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from fastapi import Depends, status

from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.users.models import DatabaseUser

from . import crud


def get_own_user(
    db=Depends(get_db),
    token=Depends(JWTBearer()),
) -> DatabaseUser:
    username = get_username(token)

    if user := crud.get_user_by_name(db, username):
        return user

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"reason": f"User {username} was not found"},
    )


def get_existing_user(
    user_id: int | t.Literal["current"],
    db=Depends(get_db),
    token=Depends(JWTBearer()),
) -> DatabaseUser:
    if user_id == "current":
        return get_own_user(db, token)

    if user := crud.get_user_by_id(db, user_id):
        return user

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"reason": f"User with id {user_id} was not found"},
    )
