# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import asyncer
import fastapi
import jwt
from fastapi import security
from jwt import exceptions as jwt_exceptions

from capellacollab.configuration.app import config

from . import exceptions, oidc

log = logging.getLogger(__name__)

auth_config = config.authentication


class JWTConfig:
    _jwks_client = None

    def __init__(self, oidc_config: oidc.OIDCProviderConfig):
        self.oidc_config = oidc_config

        if JWTConfig._jwks_client is None:
            JWTConfig._jwks_client = jwt.PyJWKClient(
                uri=self.oidc_config.get_jwks_uri()
            )
        self.jwks_client = JWTConfig._jwks_client


class JWTAPIKeyCookie(security.APIKeyCookie):
    def __init__(self):
        super().__init__(name="id_token", auto_error=True)
        self.oidc_config = oidc.get_cached_oidc_config()
        self.jwt_config = JWTConfig(self.oidc_config)

    async def __call__(self, request: fastapi.Request) -> str:
        token: str | None = await super().__call__(request)

        if not token:
            raise exceptions.UnauthenticatedError()

        token_decoded = await asyncer.asyncify(self.validate_token)(token)
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
        except jwt_exceptions.ExpiredSignatureError as e:
            raise exceptions.TokenSignatureExpired() from e
        except jwt_exceptions.InvalidIssuerError as e:
            log.exception(
                "Expected issuer '%s'. Got '%s'",
                self.oidc_config.get_issuer(),
                jwt.decode(
                    jwt=token,
                    options={"verify_signature": False},
                )["iss"],
            )
            raise exceptions.JWTValidationFailed() from e
        except jwt_exceptions.PyJWTError as e:
            log.exception("JWT validation failed")
            raise exceptions.JWTValidationFailed() from e

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
