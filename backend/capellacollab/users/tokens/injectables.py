# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t
from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, models


def get_own_user_tokens(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(user_injectables.get_own_user),
    ],
) -> abc.Sequence[models.DatabaseUserToken]:
    return crud.get_all_tokens_for_user(db, user.id)


def get_exisiting_own_user_token(
    token_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(user_injectables.get_own_user),
    ],
) -> models.DatabaseUserToken:
    token = crud.get_token_by_user_and_id(db, user.id, token_id)
    if not token:
        raise exceptions.TokenNotFoundError(token_id)
    return token
