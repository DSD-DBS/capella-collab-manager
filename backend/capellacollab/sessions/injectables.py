# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db
from capellacollab.users.models import Role

from . import database
from .models import DatabaseSession


def get_existing_session(
    session_id: str,
    db: Session = Depends(get_db),
    token: JWTBearer = Depends(JWTBearer()),
) -> DatabaseSession:
    try:
        session: DatabaseSession = database.get_session_by_id(db, session_id)
    except NoResultFound as e:
        raise HTTPException(
            404,
            {"reason": f"The session with id {session_id} was not found."},
        ) from e
    if session.owner_name != get_username(token) and not RoleVerification(
        required_role=Role.ADMIN, verify=False
    )(token, db):
        raise HTTPException(
            403,
            {
                "reason": f"The session {session.id} does not belong to your user. Only administrators can manage other sessions!"
            },
        )

    return session
