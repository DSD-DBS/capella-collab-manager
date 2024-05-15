# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, models


def get_existing_session(
    session_id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    username: str = fastapi.Depends(auth_injectables.get_username),
) -> models.DatabaseSession:
    if not (session := crud.get_session_by_id(db, session_id)):
        raise exceptions.SessionNotFoundError(session_id)
    if not (
        session.owner_name == username
        or auth_injectables.RoleVerification(
            required_role=users_models.Role.ADMIN, verify=False
        )(username, db)
    ):
        raise exceptions.SessionNotOwnedError(session_id)

    return session
