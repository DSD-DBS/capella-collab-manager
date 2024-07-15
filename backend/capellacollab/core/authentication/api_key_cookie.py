# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
import jwt
from fastapi import security
from jwt import exceptions as jwt_exceptions

from capellacollab.config import config

from . import exceptions, oidc_provider

log = logging.getLogger(__name__)


class JWTConfigBorg:
    _shared_state: dict[str, str] = {}

    def __init__(
        self, provider_config: oidc_provider.AbstractOIDCProviderConfig
    ):
        self.__dict__ = self._shared_state
        self.provider_config = provider_config

        if not hasattr(self, "jwks_client"):
            self.jwks_client = jwt.PyJWKClient(
                uri=self.provider_config.get_jwks_uri()
            )


class JWTAPIKeyCookie(security.APIKeyCookie):
    def __init__(
        self, provider_config: oidc_provider.AbstractOIDCProviderConfig
    ):
        super().__init__(name="id_token", auto_error=True)
        self.provider_config = provider_config
        self.jwt_config = JWTConfigBorg(provider_config)

    async def __call__(self, request: fastapi.Request) -> str:
        token: str | None = await super().__call__(request)

        if not token:
            raise exceptions.UnauthenticatedError()

        token_decoded = self.validate_token(token)
        return self.get_username(token_decoded)

    def get_username(self, token_decoded: dict[str, str]) -> str:
        return token_decoded[config.authentication.jwt.username_claim].strip()

    def validate_token(self, token: str) -> dict[str, t.Any]:
        try:
            signing_key = self.jwt_config.jwks_client.get_signing_key_from_jwt(
                token
            )

            return jwt.decode(
                jwt=token,
                key=signing_key.key,
                algorithms=self.provider_config.get_supported_signing_algorithms(),
                audience=self.provider_config.get_client_id(),
                issuer=self.provider_config.get_issuer(),
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                },
            )
        except jwt_exceptions.ExpiredSignatureError:
            raise exceptions.TokenSignatureExpired()
        except jwt_exceptions.PyJWTError:
            log.exception("JWT validation failed", exc_info=True)
            raise exceptions.JWTValidationFailed()
