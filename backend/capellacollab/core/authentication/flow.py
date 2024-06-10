# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import requests
from oauthlib import common, oauth2

from capellacollab.config import config

from . import exceptions

CODE_CHALLENGE_METHOD = "S256"

logger = logging.getLogger(__name__)

auth_config = config.authentication
web_client = oauth2.WebApplicationClient(client_id=auth_config.client.id)


class AuthEndpoints(t.TypedDict):
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str


def get_authorization_url_with_parameters() -> t.Tuple[str, str, str, str]:
    state = common.generate_token()
    nonce = common.generate_nonce()
    code_verifier = web_client.create_code_verifier(length=43)
    code_challenge = web_client.create_code_challenge(
        code_verifier, CODE_CHALLENGE_METHOD
    )

    auth_url = web_client.prepare_request_uri(
        uri=get_auth_endpoints()["authorization_endpoint"],
        redirect_uri=auth_config.redirect_uri,
        scope=auth_config.scopes,
        state=state,
        nonce=nonce,
        code_challenge=code_challenge,
        code_challenge_method=CODE_CHALLENGE_METHOD,
    )

    return (auth_url, state, nonce, code_verifier)


def exchange_code_for_tokens(
    authorization_code: str, code_verifier: str
) -> dict[str, t.Any]:
    token_request_body = web_client.prepare_request_body(
        code=authorization_code,
        redirect_uri=auth_config.redirect_uri,
        code_verifier=code_verifier,
        client_secret=auth_config.client.secret,
    )

    r = requests.post(
        url=get_auth_endpoints()["token_endpoint"],
        data=dict(common.urldecode(token_request_body)),
        timeout=config.requests.timeout,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    return web_client.parse_request_body_response(r.text)


def refresh_token(_refresh_token: str) -> dict[str, t.Any]:
    try:
        refresh_request_body = web_client.prepare_refresh_body(
            refresh_token=_refresh_token,
            scope=auth_config.scopes,
            client_id=auth_config.client.id,
            client_secret=auth_config.client.secret,
        )

        r = requests.post(
            url=get_auth_endpoints()["token_endpoint"],
            data=dict(common.urldecode(refresh_request_body)),
            timeout=config.requests.timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        return web_client.parse_request_body_response(
            r.text, scope=auth_config.scopes
        )
    except Exception as e:
        logger.debug("Could not refresh token because of exception %s", str(e))
        raise exceptions.RefreshTokenSignatureExpired()


def get_auth_endpoints() -> AuthEndpoints:
    well_known_req = requests.get(
        auth_config.endpoints.well_known, timeout=config.requests.timeout
    )
    well_known_req.raise_for_status()

    resp = well_known_req.json()

    authorization_endpoint = resp["authorization_endpoint"]
    if auth_config.endpoints.authorization:
        authorization_endpoint = auth_config.endpoints.authorization

    return AuthEndpoints(
        authorization_endpoint=authorization_endpoint,
        token_endpoint=resp["token_endpoint"],
        jwks_uri=resp["jwks_uri"],
    )


def get_supported_signing_algorithms() -> list[str]:
    well_known_req = requests.get(
        auth_config.endpoints.well_known, timeout=config.requests.timeout
    )
    well_known_req.raise_for_status()

    resp = well_known_req.json()

    return resp["id_token_signing_alg_values_supported"]
