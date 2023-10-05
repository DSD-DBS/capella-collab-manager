# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

from . import crud, injectables, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)


@router.post("", response_model=models.UserTokenWithPassword)
def create_token_for_user(
    post_token: models.PostToken,
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.UserTokenWithPassword:
    token, password = crud.create_token(
        db,
        user.id,
        post_token.description,
        post_token.expiration_date,
        post_token.source,
    )
    return models.UserTokenWithPassword(
        id=token.id,
        user_id=token.user_id,
        hash=token.hash,
        expiration_date=token.expiration_date,
        description=token.description,
        source=token.source,
        password=password,
    )


@router.get("", response_model=list[models.UserToken])
def get_all_tokens_of_user(
    token_list: abc.Sequence[models.DatabaseUserToken] = fastapi.Depends(
        injectables.get_own_user_tokens
    ),
) -> abc.Sequence[models.DatabaseUserToken]:
    return token_list


@router.delete("/{token_id}", status_code=204)
def delete_token_for_user(
    token: models.DatabaseUserToken = fastapi.Depends(
        injectables.get_exisiting_own_user_token
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> None:
    return crud.delete_token(db, token)
