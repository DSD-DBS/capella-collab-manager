# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.schemas import (
    RefreshTokenRequest,
    TokenRequest,
)
from capellacollab.core.database import get_db
from capellacollab.users.crud import get_user_by_name, update_last_login
from capellacollab.users.models import Role

from .flow import get_auth_redirect_url, get_token, refresh_token

router = APIRouter()


@router.get("/", name="Get redirect URL for OAuth")
async def get_redirect_url():
    return get_auth_redirect_url()


@router.post("/tokens", name="Create access_token")
async def api_get_token(body: TokenRequest, db: Session = Depends(get_db)):
    token = get_token(body.code)

    username = get_username(JWTBearer().validate_token(token["access_token"]))
    update_last_login(db, get_user_by_name(db, username))

    return token


@router.put("/tokens", name="Refresh the access_token")
async def api_refresh_token(body: RefreshTokenRequest):
    return refresh_token(body.refresh_token)


@router.delete("/tokens", name="Invalidate the token (log out)")
async def logout(jwt_decoded=Depends(JWTBearer())):
    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(
    scope: t.Optional[Role],
    token=Depends(JWTBearer()),
    db=Depends(get_db),
):
    if scope and scope.ADMIN:
        RoleVerification(required_role=Role.ADMIN)(token, db)
    return token
