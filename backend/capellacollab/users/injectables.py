# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from fastapi import Depends

from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db

from . import crud


def get_own_user(
    db=Depends(get_db),
    token=Depends(JWTBearer()),
):
    username = get_username(token)
    return crud.get_user(db, username)


def get_user(
    user_id: t.Union[int, t.Literal["current"]],
    db=Depends(get_db),
    token=Depends(JWTBearer()),
):
    if user_id == "current":
        return get_own_user(db, token)
    else:
        return crud.get_user_by_id(db, user_id)
