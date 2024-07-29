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

auth_config = config.authentication


class JWTConfig:
    _jwks_client = None

    def __init__(self, oidc_config: oidc_provider.AbstractOIDCProviderConfig):
        self.oidc_config = oidc_config

        if JWTConfig._jwks_client is None:
            JWTConfig._jwks_client = jwt.PyJWKClient(
                uri=self.oidc_config.get_jwks_uri()
            )
        self.jwks_client = JWTConfig._jwks_client


class JWTAPIKeyCookie(security.APIKeyCookie):
    def __init__(self, oidc_config: oidc_provider.AbstractOIDCProviderConfig):
        super().__init__(name="id_token", auto_error=True)
        self.oidc_config = oidc_config
        self.jwt_config = JWTConfig(oidc_config)

    async def __call__(self, request: fastapi.Request) -> str:
        token: str | None = await super().__call__(request)

        if not token:
            raise exceptions.UnauthenticatedError()

        token_decoded = self.validate_token(token)
        return self.get_username(token_decoded)

    def validate_token(self, token: str) -> dict[str, t.Any]:
        try:
            signing_key = self.jwt_config.jwks_client.get_signing_key_from_jwt(
                token
            )

            return jwt.decode(
                jwt=token,
                key=signing_key.key,
                algorithms=self.oidc_config.get_supported_signing_algorithms(),
                audience=self.oidc_config.get_client_id(),
                issuer=self.oidc_config.get_issuer(),
                options={"require": ["exp", "iat"]},
            )
        except jwt_exceptions.ExpiredSignatureError:
            raise exceptions.TokenSignatureExpired()
        except jwt_exceptions.PyJWTError:
            log.exception("JWT validation failed", exc_info=True)
            raise exceptions.JWTValidationFailed()

    @classmethod
    def get_username(cls, token_decoded: dict[str, str]) -> str:
        return token_decoded[auth_config.mapping.username].strip()

    @classmethod
    def get_idp_identifier(cls, token_decoded: dict[str, str]) -> str:
        return token_decoded[auth_config.mapping.identifier].strip()

    @classmethod
    def get_email(cls, token_decoded: dict[str, str]) -> str | None:
        if auth_config.mapping.email:
            return token_decoded.get(auth_config.mapping.email, None)
        return None
