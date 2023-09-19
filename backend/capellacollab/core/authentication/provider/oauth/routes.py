# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

import capellacollab.users.crud as users_crud
from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.authentication.jwt_bearer import JWTBearer
from capellacollab.core.authentication.schemas import (
    RefreshTokenRequest,
    TokenRequest,
)
from capellacollab.users.models import Role

from .flow import get_auth_redirect_url, get_token, refresh_token

router = fastapi.APIRouter()


@router.get("", name="Get redirect URL for OAuth")
async def get_redirect_url():
    return get_auth_redirect_url()


@router.post("/tokens", name="Create access_token")
async def api_get_token(
    body: TokenRequest, db: orm.Session = fastapi.Depends(database.get_db)
):
    token = get_token(body.code)
    access_token = token["id_token"]

    validated_token = JWTBearer().validate_token(access_token)
    assert validated_token

    username = get_username(validated_token)

    if user := users_crud.get_user_by_name(db, username):
        users_crud.update_last_login(db, user)

    return token


@router.put("/tokens", name="Refresh the access_token")
async def api_refresh_token(body: RefreshTokenRequest):
    return refresh_token(body.refresh_token)


@router.delete("/tokens", name="Invalidate the token (log out)")
async def logout():
    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(
    scope: Role | None,
    token=fastapi.Depends(JWTBearer()),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if scope and scope.ADMIN:
        auth_injectables.RoleVerification(required_role=Role.ADMIN)(token, db)
    return token
