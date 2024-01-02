# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
import typing as t

import fastapi
from fastapi import security, status
from jose import jwt

import capellacollab.users.crud as users_crud
from capellacollab.config import config
from capellacollab.core import database
from capellacollab.events import crud as events_crud

from . import get_authentication_entrypoint

log = logging.getLogger(__name__)
ep = get_authentication_entrypoint()
ep_main = importlib.import_module(".__main__", ep.module)


class JWTBearer(security.HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(  # type: ignore
        self, request: fastapi.Request
    ) -> str | None:
        credentials: security.HTTPAuthorizationCredentials | None = (
            await super().__call__(request)
        )

        if not credentials or credentials.scheme != "Bearer":
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer, Basic"},
                )
            return None
        if token_decoded := self.validate_token(credentials.credentials):
            self.initialize_user(token_decoded)
            return self.get_username(token_decoded)
        if self.auto_error:
            raise fastapi.HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer, Basic"},
            )
        return None

    def get_username(self, token_decoded: dict[str, str]) -> str:
        return token_decoded[
            config["authentication"]["jwt"]["usernameClaim"]
        ].strip()

    def initialize_user(self, token_decoded: dict[str, str]):
        with database.SessionLocal() as session:
            username: str = self.get_username(token_decoded)
            if not users_crud.get_user_by_name(session, username):
                created_user = users_crud.create_user(session, username)
                users_crud.update_last_login(session, created_user)
                events_crud.create_user_creation_event(session, created_user)

    def validate_token(self, token: str) -> dict[str, t.Any] | None:
        try:
            jwt_cfg = ep_main.get_jwk_cfg(token)
        except Exception:
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "err_code": "JWT_TOKEN_INVALID",
                        "reason": "The used token is not valid.",
                    },
                ) from None
            return None
        try:
            return jwt.decode(token, **jwt_cfg)
        except jwt.ExpiredSignatureError:
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "err_code": "token_exp",
                        "reason": "The Signature of the token is expired. Please request a new access token.",
                    },
                ) from None
            return None
        except (jwt.JWTError, jwt.JWTClaimsError):
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "technical": "The validation of your access token failed. Please contact your administrator.",
                    },
                ) from None
            return None
