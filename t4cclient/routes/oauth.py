from fastapi import APIRouter, Depends, Request
from t4cclient.core.oauth import (
    jwt_bearer,
    refresh_token
)
from t4cclient.schemas.oauth import RefreshTokenRequest, TokenRequest

router = APIRouter()

import typing as t

from fastapi import Depends, Request
from msal import ConfidentialClientApplication
from t4cclient.config import (
    OAUTH_CLIENT_ID,
    OAUTH_CLIENT_SECRET,
    OAUTH_ENDPOINT,
)


ad_session = ConfidentialClientApplication(OAUTH_CLIENT_ID, client_credential=OAUTH_CLIENT_SECRET, authority=OAUTH_ENDPOINT)


# WARN: This might be a security risk:
global_session_data = {}


@router.get("/", name="Get redirect URL for OAuth")
async def get_redirect_url():
    session_data = ad_session.initiate_auth_code_flow(scopes=[])
    global_session_data[session_data["state"]] = session_data
    return {"auth_url": session_data["auth_uri"], "state": session_data["state"]}


@router.post("/tokens", name="Create access_token")
async def api_get_token(body: TokenRequest):
    auth_data = global_session_data[body.state]
    del global_session_data[body.state]
    token = ad_session.acquire_token_by_auth_code_flow(auth_data, body.dict(), scopes=[])
    return token


@router.put("/tokens", name="Refresh the access_token")
async def api_refresh_token(body: RefreshTokenRequest):
    return refresh_token(body.refresh_token)


@router.get("/tokens", name="Validate the token")
async def validate_token(jwt_decoded=Depends(jwt_bearer.JWTBearer())):
    return jwt_decoded
