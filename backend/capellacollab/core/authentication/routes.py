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

from . import api_key_cookie, exceptions, injectables, models, oidc_provider

router = fastapi.APIRouter()


@router.get("", name="Get the authorization URL for the OAuth Server")
async def get_redirect_url(
    response: fastapi.Response,
    provider: oidc_provider.AbstractOIDCProvider = fastapi.Depends(
        injectables.get_oidc_provider
    ),
) -> dict[str, str]:
    auth_url, state, nonce, code_verifier = (
        provider.get_authorization_url_with_parameters()
    )
    delete_token_cookies(response)

    return {
        "auth_url": auth_url,
        "state": state,
        "nonce": nonce,
        "code_verifier": code_verifier,
    }


@router.post("/tokens", name="Create the identity token")
async def api_get_token(
    token_request: models.TokenRequest,
    response: fastapi.Response,
    db: orm.Session = fastapi.Depends(database.get_db),
    provider: oidc_provider.AbstractOIDCProvider = fastapi.Depends(
        injectables.get_oidc_provider
    ),
    provider_config: oidc_provider.AbstractOIDCProviderConfig = fastapi.Depends(
        injectables.get_oidc_provider_config
    ),
):
    tokens = provider.exchange_code_for_tokens(
        token_request.code, token_request.code_verifier
    )

    user = validate_id_token(
        db, tokens["id_token"], provider_config, token_request.nonce
    )

    update_token_cookies(
        response, tokens["id_token"], tokens.get("refresh_token", None), user
    )


@router.put("/tokens", name="Refresh the identity token")
async def api_refresh_token(
    response: fastapi.Response,
    refresh_token: t.Annotated[str | None, fastapi.Cookie()] = None,
    db: orm.Session = fastapi.Depends(database.get_db),
    provider: oidc_provider.AbstractOIDCProvider = fastapi.Depends(
        injectables.get_oidc_provider
    ),
    provider_config: oidc_provider.AbstractOIDCProviderConfig = fastapi.Depends(
        injectables.get_oidc_provider_config
    ),
):
    if refresh_token is None or refresh_token == "":
        raise exceptions.RefreshTokenCookieMissingError()

    tokens = provider.refresh_token(refresh_token)

    user = validate_id_token(db, tokens["id_token"], provider_config, None)
    update_token_cookies(
        response, tokens["id_token"], tokens.get("refresh_token", None), user
    )


@router.delete("/tokens", name="Remove the token (log out)")
async def logout(response: fastapi.Response):
    delete_token_cookies(response)
    return None


@router.get("/tokens", name="Validate the token")
async def validate_token(
    request: fastapi.Request,
    scope: users_models.Role | None = None,
    db: orm.Session = fastapi.Depends(database.get_db),
    provider_config: oidc_provider.AbstractOIDCProviderConfig = fastapi.Depends(
        injectables.get_oidc_provider_config
    ),
):
    username = await api_key_cookie.JWTAPIKeyCookie(provider_config)(request)
    if scope and scope.ADMIN:
        auth_injectables.RoleVerification(
            required_role=users_models.Role.ADMIN
        )(username, db)
    return username


def validate_id_token(
    db: orm.Session,
    id_token: str,
    provider_config: oidc_provider.AbstractOIDCProviderConfig,
    nonce: str | None,
) -> users_models.DatabaseUser:
    validated_id_token = api_key_cookie.JWTAPIKeyCookie(
        provider_config
    ).validate_token(id_token)

    if nonce and not hmac.compare_digest(validated_id_token["nonce"], nonce):
        raise exceptions.NonceMismatchError()

    if provider_config.get_client_id() not in validated_id_token["aud"]:
        raise exceptions.UnauthenticatedError()

    username = api_key_cookie.JWTAPIKeyCookie(provider_config).get_username(
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
