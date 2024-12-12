# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, models, util


def get_existing_session(
    session_id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    global_scope: permissions_models.GlobalScopes = fastapi.Depends(
        permissions_injectables.get_scope
    ),
) -> models.DatabaseSession:
    """Get a session by its ID, ensuring that the user is the owner or an admin."""

    if not (session := crud.get_session_by_id(db, session_id)):
        raise exceptions.SessionNotFoundError(session_id)
    if (
        session.owner.id != user.id
        and permissions_models.UserTokenVerb.GET
        not in global_scope.admin.sessions
    ):
        raise exceptions.SessionNotOwnedError(session_id)

    return session


def get_existing_session_including_shared(
    session_id: str,
    db: orm.Session = fastapi.Depends(database.get_db),
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    global_scope: permissions_models.GlobalScopes = fastapi.Depends(
        permissions_injectables.get_scope
    ),
) -> models.DatabaseSession:
    if not (session := crud.get_session_by_id(db, session_id)):
        raise exceptions.SessionNotFoundError(session_id)
    if (
        session.owner.id != user.id
        and not util.is_session_shared_with_user(session, user)
        and permissions_models.UserTokenVerb.GET
        not in global_scope.admin.sessions
    ):
        raise exceptions.SessionNotOwnedError(session_id)

    return session
