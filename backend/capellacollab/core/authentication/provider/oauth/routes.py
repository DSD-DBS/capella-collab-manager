# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends

import typing as t

from fastapi import APIRouter, Depends

from .flow import get_auth_redirect_url, get_token, refresh_token
from capellacollab.core.authentication import jwt_bearer
from capellacollab.core.authentication.database import verify_admin
from capellacollab.core.authentication.schemas import RefreshTokenRequest, TokenRequest
from capellacollab.core.database import get_db
from capellacollab.projects.users.models import Role

router = APIRouter()


@router.get("/", name="Get redirect URL for OAuth")
async def get_redirect_url():
    return get_auth_redirect_url()


@router.post("/tokens", name="Create access_token")
async def api_get_token(body: TokenRequest):
    return get_token(body.code)


@router.put("/tokens", name="Refresh the access_token")
async def api_refresh_token(body: RefreshTokenRequest):
    return refresh_token(body.refresh_token)


@router.delete("/tokens", name="Invalidate the token (log out)")
async def logout(jwt_decoded=Depends(jwt_bearer.JWTBearer())):
    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(
    scope: t.Optional[Role], token=Depends(jwt_bearer.JWTBearer()), db=Depends(get_db)
):
    if scope.ADMIN:
        verify_admin(token, db)
    return token
