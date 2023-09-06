# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_models

from . import crud

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.USER
            )
        )
    ]
)


@router.post("/current/token")
def create_token_for_user(
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
    description: str = fastapi.Body(),
):
    _, password = crud.create_token(db, user.id, description)
    return password


@router.get("/current/tokens")
def get_all_token_of_user(
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    return crud.get_token_by_user(db, user.id)


@router.delete("/current/token/{id}")
def delete_token_for_user(
    id: int,
    user: users_models.DatabaseUser = fastapi.Depends(
        user_injectables.get_own_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    token_list = crud.get_token_by_user(db, user.id)
    if token_list:
        token = [token for token in token_list if token.id == id][0]
        return crud.delete_token(db, token)
    return None
