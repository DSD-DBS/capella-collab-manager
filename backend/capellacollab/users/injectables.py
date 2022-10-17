# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends

from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.database import get_db

from . import crud


def get_own_user(
    db=Depends(get_db),
    token=Depends(JWTBearer()),
):
    username = get_username(token)
    return crud.get_user(db, username)
