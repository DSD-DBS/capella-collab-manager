# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# Standard library:
import typing as t

# 3rd party:
from fastapi import APIRouter, Depends

# local:
from .flow import get_auth_redirect_url, get_token, refresh_token
from t4cclient.core.authentication import jwt_bearer
from t4cclient.core.authentication.database import verify_admin
from t4cclient.core.authentication.schemas import RefreshTokenRequest, TokenRequest
from t4cclient.core.database import get_db
from t4cclient.schemas.repositories.users import Role

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
