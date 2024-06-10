# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
import jwt
from fastapi import security
from jwt import exceptions as jwt_exceptions

from capellacollab.config import config

from . import exceptions, flow

log = logging.getLogger(__name__)


class JWTConfigBorg:
    _shared_state: dict[str, str] = {}

    def __init__(self) -> None:
        self.__dict__ = self._shared_state

        if not hasattr(self, "_jwks_client"):
            self.jwks_client = jwt.PyJWKClient(
                uri=flow.get_auth_endpoints()["jwks_uri"]
            )

        if not hasattr(self, "_supported_signing_algorithms"):
            self.supported_signing_algorithms = (
                flow.get_supported_signing_algorithms()
            )


class JWTAPIKeyCookie(security.APIKeyCookie):
    def __init__(self):
        super().__init__(name="id_token", auto_error=True)
        self.jwt_config = JWTConfigBorg()

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
                algorithms=self.jwt_config.supported_signing_algorithms,
                audience=config.authentication.client.id,
                issuer=config.authentication.issuer,
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
