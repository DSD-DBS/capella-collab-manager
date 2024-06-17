# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
from fastapi import security
from jose import exceptions as jwt_exceptions
from jose import jwt

from capellacollab.config import config

from . import exceptions, keystore

log = logging.getLogger(__name__)


class JWTAPIKeyCookie(security.APIKeyCookie):
    def __init__(self):
        super().__init__(name="id_token", auto_error=True)

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
            jwt_cfg = keystore.get_jwk_cfg(token)
        except Exception:
            log.exception(
                "Couldn't determine JWK configuration", exc_info=True
            )
            raise exceptions.JWTInvalidToken()
        try:
            return jwt.decode(token, **jwt_cfg)
        except jwt_exceptions.ExpiredSignatureError:
            raise exceptions.TokenSignatureExpired()
        except (jwt_exceptions.JWTError, jwt_exceptions.JWTClaimsError):
            log.exception("JWT validation failed", exc_info=True)
            raise exceptions.JWTValidationFailed()
