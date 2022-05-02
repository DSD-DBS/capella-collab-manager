# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import secrets
import typing as t
from functools import lru_cache

from cachetools import TTLCache
from fastapi import APIRouter, Depends
from msal import ConfidentialClientApplication
from t4cclient.config import config
from t4cclient.core.authentication import jwt_bearer
from t4cclient.core.authentication.schemas import RefreshTokenRequest, TokenRequest

router = APIRouter()
cfg = config["authentication"]["azure"]


@lru_cache()
def ad_session():
    return ConfidentialClientApplication(
        cfg["client"]["id"],
        client_credential=cfg["client"]["secret"],
        authority=cfg["connectConfigurationEndpoint"],
    )


# Make this a cache:
global_session_data = TTLCache(maxsize=128, ttl=3600)


@router.get("/", name="Get redirect URL for azure authentication")
async def get_redirect_url():
    state = secrets.token_hex(32)
    assert state not in global_session_data
    session_data = ad_session().initiate_auth_code_flow(scopes=[], state=state)
    global_session_data[session_data["state"]] = session_data
    return {"auth_url": session_data["auth_uri"], "state": session_data["state"]}


@router.post("/tokens", name="Create access_token")
async def api_get_token(body: TokenRequest):
    auth_data = global_session_data[body.state]
    del global_session_data[body.state]
    token = ad_session().acquire_token_by_auth_code_flow(
        auth_data, body.dict(), scopes=[]
    )

    # *Sigh* This is microsoft again. Instead of the access_token, we should use id_token :/
    # https://stackoverflow.com/questions/63195081/how-to-validate-a-jwt-from-azuread-in-python
    return {
        "access_token": token["id_token"],
        "refresh_token": token["refresh_token"],
        "token_type": token["token_type"],
    }


@router.put("/tokens", name="Refresh the access_token")
async def api_refresh_token(body: RefreshTokenRequest):
    return ad_session().acquire_token_by_refresh_token(body.refresh_token, scopes=[])


@router.delete("/tokens", name="Invalidate the token (log out)")
async def logout(jwt_decoded=Depends(jwt_bearer.JWTBearer())):
    for account in ad_session().get_accounts():
        if account["username"] == jwt_decoded["preferred_username"]:
            return ad_session().remove_account(account)
    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(jwt_decoded=Depends(jwt_bearer.JWTBearer())):
    return jwt_decoded
