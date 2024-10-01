# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import functools
import logging
import typing as t

import requests
from oauthlib import common, oauth2

from capellacollab.config import config

from . import exceptions, models

logger = logging.getLogger(__name__)


class OIDCProviderConfig:
    def __init__(self):
        self.well_known_uri = config.authentication.endpoints.well_known
        self.well_known = self._fetch_well_known_configuration()

    def _fetch_well_known_configuration(self):
        well_known_req = requests.get(
            self.well_known_uri, timeout=config.requests.timeout
        )
        well_known_req.raise_for_status()

        return well_known_req.json()

    def get_authorization_endpoint(self) -> str:
        return (
            config.authentication.endpoints.authorization
            or self.well_known.get("authorization_endpoint")
        )

    def get_token_endpoint(self) -> str:
        return self.well_known.get("token_endpoint")

    def get_jwks_uri(self) -> str:
        return self.well_known.get("jwks_uri")

    def get_supported_signing_algorithms(self) -> list[str]:
        return self.well_known.get("id_token_signing_alg_values_supported")

    def get_issuer(self) -> str:
        return self.well_known_uri.removesuffix(
            "/.well-known/openid-configuration"
        )

    def get_scopes(self) -> list[str]:
        return config.authentication.scopes

    def get_client_secret(self) -> str:
        return config.authentication.client.secret

    def get_client_id(self) -> str:
        return config.authentication.client.id


@functools.lru_cache
def get_cached_oidc_config() -> OIDCProviderConfig:
    return OIDCProviderConfig()


class OIDCProvider:
    CODE_CHALLENGE_METHOD = "S256"

    def __init__(self):
        self.oidc_config = get_cached_oidc_config()
        self.web_client: oauth2.WebApplicationClient = (
            oauth2.WebApplicationClient(
                client_id=self.oidc_config.get_client_id()
            )
        )

    def get_authorization_url_with_parameters(
        self,
    ) -> models.AuthorizationResponse:
        state = common.generate_token()
        nonce = common.generate_nonce()

        code_verifier = self.web_client.create_code_verifier(length=43)
        code_challenge = self.web_client.create_code_challenge(
            code_verifier, OIDCProvider.CODE_CHALLENGE_METHOD
        )

        auth_url = self.web_client.prepare_request_uri(
            uri=self.oidc_config.get_authorization_endpoint(),
            redirect_uri=config.authentication.redirect_uri,
            scope=self.oidc_config.get_scopes(),
            state=state,
            nonce=nonce,
            code_challenge=code_challenge,
            code_challenge_method=OIDCProvider.CODE_CHALLENGE_METHOD,
        )

        return models.AuthorizationResponse(
            auth_url=auth_url,
            state=state,
            nonce=nonce,
            code_verifier=code_verifier,
        )

    def exchange_code_for_tokens(
        self, authorization_code: str, code_verifier: str
    ) -> dict[str, t.Any]:
        token_request_body = self.web_client.prepare_request_body(
            code=authorization_code,
            redirect_uri=config.authentication.redirect_uri,
            code_verifier=code_verifier,
            client_secret=self.oidc_config.get_client_secret(),
        )

        r = requests.post(
            url=self.oidc_config.get_token_endpoint(),
            data=dict(common.urldecode(token_request_body)),
            timeout=config.requests.timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        return self.web_client.parse_request_body_response(r.text)

    def refresh_token(self, _refresh_token: str) -> dict[str, t.Any]:
        try:
            refresh_request_body = self.web_client.prepare_refresh_body(
                refresh_token=_refresh_token,
                scope=self.oidc_config.get_scopes(),
                client_id=self.oidc_config.get_client_id(),
                client_secret=self.oidc_config.get_client_secret(),
            )

            r = requests.post(
                url=self.oidc_config.get_token_endpoint(),
                data=dict(common.urldecode(refresh_request_body)),
                timeout=config.requests.timeout,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

            return self.web_client.parse_request_body_response(
                r.text, scope=self.oidc_config.get_scopes()
            )
        except Exception:
            logger.info("Could not refresh token", exc_info=True)
            raise exceptions.RefreshTokenSignatureExpired()
