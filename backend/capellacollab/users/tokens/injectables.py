# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

from . import crud, models


def get_own_user_tokens(
    db: orm.Session = fastapi.Depends(database.get_db),
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
) -> abc.Sequence[models.DatabaseUserToken]:
    return crud.get_token_by_user(db, user.id)


def get_exisiting_own_user_token(
    token_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
) -> models.DatabaseUserToken:
    token = crud.get_token_by_user_and_id(db, user.id, token_id)
    if not token:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )
    return token
