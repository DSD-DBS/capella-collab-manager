# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import logging
import typing as t

import fastapi
import requests
from fastapi import status
from requests_oauthlib import OAuth2Session

from capellacollab.config import config
from capellacollab.config import models as config_models

assert isinstance(
    config.authentication, config_models.OAuthAuthenticationConfig
)
cfg = config.authentication.oauth

logger = logging.getLogger(__name__)


auth_args = {}
if cfg.scopes:
    auth_args["scope"] = cfg.scopes

auth_session = OAuth2Session(
    cfg.client.id, redirect_uri=cfg.redirect_uri, **auth_args
)


def get_auth_redirect_url() -> dict[str, str]:
    auth_url, state = auth_session.authorization_url(
        read_well_known()["authorization_endpoint"],
        grant_type="authorization_code",
    )

    return {"auth_url": auth_url, "state": state}


def get_token(code: str) -> dict[str, t.Any]:
    return auth_session.fetch_token(
        read_well_known()["token_endpoint"],
        code=code,
        client_id=cfg.client.id,
        client_secret=cfg.client.secret,
    )


def refresh_token(_refresh_token: str) -> dict[str, t.Any]:
    try:
        return auth_session.refresh_token(
            read_well_known()["token_endpoint"],
            refresh_token=_refresh_token,
            client_id=cfg.client.id,
            client_secret=cfg.client.secret,
        )
    except Exception as e:
        logger.debug("Could not refresh token because of exception %s", str(e))
        raise fastapi.HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "err_code": "REQUEST_TOKEN_EXPIRED",
                "reason": "The Signature of the refresh token is expired. Please request a new access token.",
            },
        )


def read_well_known() -> dict[str, t.Any]:
    authorization_endpoint = None
    token_endpoint = None

    if cfg.endpoints.well_known:
        r = requests.get(
            cfg.endpoints.well_known,
            timeout=config.requests.timeout,
        )
        r.raise_for_status()

        resp = r.json()

        authorization_endpoint = resp["authorization_endpoint"]
        token_endpoint = resp["token_endpoint"]

    if cfg.endpoints.authorization:
        authorization_endpoint = cfg.endpoints.authorization

    if cfg.endpoints.token_issuance:
        token_endpoint = cfg.endpoints.token_issuance

    return {
        "authorization_endpoint": authorization_endpoint,
        "token_endpoint": token_endpoint,
    }
