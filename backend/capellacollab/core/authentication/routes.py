# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.config import config
from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.events import crud as events_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

from . import api_key_cookie, exceptions, flow, models

router = fastapi.APIRouter()


@router.get("", name="Get redirect URL for Auth Server")
async def get_redirect_url(response: fastapi.Response) -> dict[str, str]:
    auth_url, state, nonce, code_verifier = (
        flow.get_authorization_url_with_parameters()
    )

    delete_token_cookies(response)

    set_secure_cookie(response, "nonce", nonce, "/api/v1")
    set_secure_cookie(response, "code_verifier", code_verifier, "/api/v1")

    return {"auth_url": auth_url, "state": state}


@router.post("/tokens", name="Create the identity token")
async def api_get_token(
    token_request: models.TokenRequest,
    response: fastapi.Response,
    nonce: t.Annotated[str | None, fastapi.Cookie()] = None,
    code_verifier: t.Annotated[str | None, fastapi.Cookie()] = None,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    delete_secure_cookie(response, "nonce", "/api/v1")
    delete_secure_cookie(response, "code_verifier", "/api/v1")

    if not nonce:
        raise exceptions.RequiredCookieMissingError(cookie_name="nonce")
    if not code_verifier:
        raise exceptions.RequiredCookieMissingError(
            cookie_name="code_verifier"
        )

    tokens = flow.exchange_code_for_tokens(token_request.code, code_verifier)

    user = validate_id_token(db, tokens["id_token"], nonce)
    update_token_cookies(
        response, tokens["id_token"], tokens["refresh_token"], user
    )

    return True


@router.put("/tokens", name="Refresh the identity token")
async def api_refresh_token(
    refresh_token: t.Annotated[str | None, fastapi.Cookie()],
    response: fastapi.Response,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if not refresh_token:
        delete_token_cookies(response)
        raise exceptions.RefreshTokenCookieMissingError()

    tokens = flow.refresh_token(refresh_token)

    user = validate_id_token(db, tokens["id_token"])
    update_token_cookies(
        response, tokens["id_token"], tokens["refresh_token"], user
    )

    return True


@router.delete("/tokens", name="Invalidate the token (log out)")
async def logout(response: fastapi.Response):
    delete_token_cookies(response)

    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(
    scope: users_models.Role | None = None,
    username: str = fastapi.Depends(api_key_cookie.JWTAPIKeyCookie()),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    if scope and scope.ADMIN:
        auth_injectables.RoleVerification(
            required_role=users_models.Role.ADMIN
        )(username, db)
    return username


def validate_id_token(
    db: orm.Session, id_token: str, nonce: str | None = None
) -> users_models.DatabaseUser:
    validated_id_token = api_key_cookie.JWTAPIKeyCookie().validate_token(
        id_token
    )

    if nonce and validated_id_token["nonce"] != nonce:
        raise exceptions.NonceMismatchError()

    assert validated_id_token
    username = api_key_cookie.JWTAPIKeyCookie().get_username(
        validated_id_token
    )

    user = users_crud.get_user_by_name(db, username)
    if not user:
        user = users_crud.create_user(db, username)
        events_crud.create_user_creation_event(db, user)

    users_crud.update_last_login(db, user)

    return user


def update_token_cookies(
    response: fastapi.Response,
    id_token: str,
    refresh_token: str,
    user: users_models.DatabaseUser,
) -> None:
    set_secure_cookie(response, "id_token", id_token, "/api/v1")
    set_secure_cookie(response, "refresh_token", refresh_token, "/api/v1")

    if user.role == users_models.Role.ADMIN:
        set_secure_cookie(response, "id_token", id_token, "/grafana")
        set_secure_cookie(response, "id_token", id_token, "/prometheus")


def delete_token_cookies(response: fastapi.Response):
    delete_secure_cookie(response, "id_token", "/api/v1")
    delete_secure_cookie(response, "id_token", "/prometheus")
    delete_secure_cookie(response, "id_token", "/grafana")
    delete_secure_cookie(response, "refresh_token", "/api/v1")


def set_secure_cookie(
    response: fastapi.Response, key: str, value: str, path: str
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        path=path,
        samesite="strict",
        httponly=True,
        expires=None,
        secure=config.general.scheme == "https",
        domain=config.general.host,
    )


def delete_secure_cookie(
    response: fastapi.Response, key: str, path: str
) -> None:
    response.delete_cookie(
        key=key,
        path=path,
        samesite="strict",
        httponly=True,
        secure=config.general.scheme == "https",
        domain=config.general.host,
    )
