from fastapi import APIRouter, Depends
from t4cclient.core.authentication import jwt_bearer
from t4cclient.core.authentication.schemas import (RefreshTokenRequest,
                                                   TokenRequest)

from .flow import get_auth_redirect_url, get_token, refresh_token

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
async def validate_token(jwt_decoded=Depends(jwt_bearer.JWTBearer())):
    return jwt_decoded
