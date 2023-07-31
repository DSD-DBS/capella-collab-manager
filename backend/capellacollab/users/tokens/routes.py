# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import credentials, database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import injectables as user_injectables
from capellacollab.users import models as users_model

from . import crud

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_model.Role.ADMIN
            )
        )
    ]
)


@router.get("/{user_id}/token")
def get_token_for_user(
    user: users_model.DatabaseUser = fastapi.Depends(
        user_injectables.get_existing_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    new_token = credentials.generate_password(32)
    crud.create_token(db, user.id, new_token, "new_token")
    return new_token
