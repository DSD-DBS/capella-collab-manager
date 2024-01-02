# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import secrets
from functools import lru_cache

import fastapi
from cachetools import TTLCache
from msal import ConfidentialClientApplication
from sqlalchemy import orm

import capellacollab.users.crud as users_crud
from capellacollab.config import config
from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.authentication import jwt_bearer
from capellacollab.core.authentication.schemas import (
    RefreshTokenRequest,
    TokenRequest,
)
from capellacollab.users.models import Role

router = fastapi.APIRouter()
cfg = config["authentication"]["azure"]


@lru_cache
def ad_session():
    return ConfidentialClientApplication(
        cfg["client"]["id"],
        client_credential=cfg["client"]["secret"],
        authority=cfg["authorizationEndpoint"],
    )


# Make this a cache:
global_session_data = TTLCache(maxsize=128, ttl=3600)


@router.get("", name="Get redirect URL for azure authentication")
async def get_redirect_url():
    state = secrets.token_hex(32)
    assert state not in global_session_data
    session_data = ad_session().initiate_auth_code_flow(scopes=[], state=state)
    global_session_data[session_data["state"]] = session_data
    return {
        "auth_url": session_data["auth_uri"],
        "state": session_data["state"],
    }


@router.post("/tokens", name="Create access_token")
async def api_get_token(
    body: TokenRequest, db: orm.Session = fastapi.Depends(database.get_db)
):
    auth_data = global_session_data[body.state]
    del global_session_data[body.state]
    token = ad_session().acquire_token_by_auth_code_flow(
        auth_data, body.model_dump(), scopes=[]
    )
    access_token = token["id_token"]

    validated_token = jwt_bearer.JWTBearer().validate_token(access_token)
    assert validated_token

    username = jwt_bearer.JWTBearer().get_username(validated_token)

    if user := users_crud.get_user_by_name(db, username):
        users_crud.update_last_login(db, user)

    # *Sigh* This is microsoft again. Instead of the access_token, we should use id_token :/
    # https://stackoverflow.com/questions/63195081/how-to-validate-a-jwt-from-azuread-in-python
    return {
        "access_token": access_token,
        "refresh_token": token["refresh_token"],
        "token_type": token["token_type"],
    }


@router.put("/tokens", name="Refresh the access_token")
async def api_refresh_token(body: RefreshTokenRequest):
    return ad_session().acquire_token_by_refresh_token(
        body.refresh_token, scopes=[]
    )


@router.delete("/tokens", name="Invalidate the token (log out)")
async def logout(username: str = fastapi.Depends(jwt_bearer.JWTBearer())):
    for account in ad_session().get_accounts():
        if account["username"] == username:
            return ad_session().remove_account(account)
    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(
    scope: Role | None,
    username: str = fastapi.Depends(jwt_bearer.JWTBearer()),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if scope and scope.ADMIN:
        auth_injectables.RoleVerification(required_role=Role.ADMIN)(
            username, db
        )
    return username
