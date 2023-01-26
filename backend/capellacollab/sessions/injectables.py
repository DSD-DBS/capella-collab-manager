# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.users.models import Role

from . import crud
from .models import DatabaseSession


def get_existing_session(
    session_id: str,
    db: Session = Depends(get_db),
    token=Depends(JWTBearer()),
) -> DatabaseSession:
    if not (session := crud.get_session_by_id(db, session_id)):
        raise HTTPException(
            404,
            {"reason": f"The session with id {session_id} was not found."},
        )
    if not (
        session.owner_name == get_username(token)
        or auth_injectables.RoleVerification(
            required_role=Role.ADMIN, verify=False
        )(token, db)
    ):
        raise HTTPException(
            403,
            {
                "reason": f"The session with id {session.id} does not belong to your user. Only administrators can manage other sessions!"
            },
        )

    return session
