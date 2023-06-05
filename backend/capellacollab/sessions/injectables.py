# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import helper as auth_helper
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication import jwt_bearer
from capellacollab.users import models as users_models

from . import crud, models


def get_existing_session(
    session_id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    token=fastapi.Depends(jwt_bearer.JWTBearer()),
) -> models.DatabaseSession:
    if not (session := crud.get_session_by_id(db, session_id)):
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The session with id {session_id} was not found."
            },
        )
    if not (
        session.owner_name == auth_helper.get_username(token)
        or auth_injectables.RoleVerification(
            required_role=users_models.Role.ADMIN, verify=False
        )(token, db)
    ):
        raise fastapi.HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "reason": f"The session with id {session.id} does not belong to your user. Only administrators can manage other sessions!"
            },
        )

    return session
