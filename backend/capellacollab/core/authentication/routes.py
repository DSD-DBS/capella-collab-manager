# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import hmac
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database, responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.events import crud as events_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

from . import api_key_cookie, exceptions, models, oidc

router = fastapi.APIRouter(tags=["Authentication"])


@router.get("")
async def get_authorization_url(
    response: fastapi.Response,
) -> models.AuthorizationResponse:
    authorization_response = (
        oidc.OIDCProvider().get_authorization_url_with_parameters()
    )
    delete_token_cookies(response)

    return authorization_response


@router.post("/tokens")
async def get_identity_token(
    token_request: models.TokenRequest,
    response: fastapi.Response,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    tokens = oidc.OIDCProvider().exchange_code_for_tokens(
        token_request.code, token_request.code_verifier
    )

    validated_id_token = validate_id_token(tokens["id_token"], None)
    user = create_or_update_user(db, validated_id_token)

    update_token_cookies(
        response, tokens["id_token"], tokens.get("refresh_token", None), user
    )


@router.put("/tokens")
async def refresh_identity_token(
    response: fastapi.Response,
    refresh_token: t.Annotated[str | None, fastapi.Cookie()] = None,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> None:
    if refresh_token is None or refresh_token == "":
        raise exceptions.RefreshTokenCookieMissingError()

    tokens = oidc.OIDCProvider().refresh_token(refresh_token)

    validated_id_token = validate_id_token(tokens["id_token"], None)
    user = create_or_update_user(db, validated_id_token)

    update_token_cookies(
        response, tokens["id_token"], tokens.get("refresh_token", None), user
    )


@router.delete("/tokens")
async def logout(response: fastapi.Response):
    delete_token_cookies(response)
    return None


@router.get("/tokens")
async def validate_jwt_token(
    request: fastapi.Request,
    scope: users_models.Role | None = None,
    db: orm.Session = fastapi.Depends(database.get_db),
):
    username = await api_key_cookie.JWTAPIKeyCookie()(request)
    if scope and scope.ADMIN:
        auth_injectables.RoleVerification(
            required_role=users_models.Role.ADMIN
        )(username, db)
    return username


def validate_id_token(
    id_token: str,
    nonce: str | None,
) -> dict[str, str]:
    validated_id_token = api_key_cookie.JWTAPIKeyCookie().validate_token(
        id_token
    )
    oidc_config = oidc.get_cached_oidc_config()

    if nonce and not hmac.compare_digest(validated_id_token["nonce"], nonce):
        raise exceptions.NonceMismatchError()

    if oidc_config.get_client_id() not in validated_id_token["aud"]:
        raise exceptions.UnauthenticatedError()

    return validated_id_token


def create_or_update_user(
    db: orm.Session, validated_id_token: dict[str, str]
) -> users_models.DatabaseUser:
    username = api_key_cookie.JWTAPIKeyCookie.get_username(validated_id_token)
    idp_identifier = api_key_cookie.JWTAPIKeyCookie.get_idp_identifier(
        validated_id_token
    )
    email = api_key_cookie.JWTAPIKeyCookie.get_email(validated_id_token)

    user = users_crud.get_user_by_idp_identifier(db, idp_identifier)
    if not user:
        user = users_crud.create_user(db, username, idp_identifier, email)
        events_crud.create_user_creation_event(db, user)

    if user.email != email:
        user = users_crud.update_user(
            db, user, users_models.PatchUser(email=email)
        )

    if user.name != username:
        user = users_crud.update_user(
            db, user, users_models.PatchUser(name=username)
        )

    users_crud.update_last_login(db, user)

    return user


def update_token_cookies(
    response: fastapi.Response,
    id_token: str,
    refresh_token: str | None,
    user: users_models.DatabaseUser,
) -> None:
    responses.set_secure_cookie(response, "id_token", id_token, "/api/v1")

    if refresh_token:
        responses.set_secure_cookie(
            response, "refresh_token", refresh_token, "/api/v1"
        )

    if user.role == users_models.Role.ADMIN:
        responses.set_secure_cookie(response, "id_token", id_token, "/grafana")
        responses.set_secure_cookie(
            response, "id_token", id_token, "/prometheus"
        )


def delete_token_cookies(response: fastapi.Response):
    responses.delete_secure_cookie(response, "id_token", "/api/v1")
    responses.delete_secure_cookie(response, "id_token", "/prometheus")
    responses.delete_secure_cookie(response, "id_token", "/grafana")
    responses.delete_secure_cookie(response, "refresh_token", "/api/v1")
