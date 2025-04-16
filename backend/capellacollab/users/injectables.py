# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users.tokens import models as tokens_models

from . import crud, exceptions, models


def get_own_user(
    authentication_information: t.Annotated[
        tuple[models.DatabaseUser, tokens_models.DatabaseUserToken | None],
        fastapi.Depends(
            auth_injectables.authentication_information_validation
        ),
    ],
) -> models.DatabaseUser:
    user = authentication_information[0]
    if user.blocked:
        raise exceptions.UserBlockedError()
    return user


def get_existing_user(
    user_id: int,
    db=fastapi.Depends(database.get_db),
) -> models.DatabaseUser:
    if user := crud.get_user_by_id(db, user_id):
        return user

    raise exceptions.UserNotFoundError(user_id=user_id)
