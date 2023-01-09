# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import importlib
import logging
import typing as t

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt

import capellacollab.users.crud as users_crud
import capellacollab.users.events.crud as events
from capellacollab.core.authentication.helper import get_username
from capellacollab.core.database import SessionLocal

from . import get_authentication_entrypoint

log = logging.getLogger(__name__)
ep = get_authentication_entrypoint()
ep_main = importlib.import_module(".__main__", ep.module)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(
        self, request: Request
    ) -> t.Optional[t.Dict[str, t.Any]]:
        credentials: t.Optional[HTTPAuthorizationCredentials] = await super(
            JWTBearer, self
        ).__call__(request)

        if not credentials or credentials.scheme != "Bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        if token_decoded := self.validate_token(credentials.credentials):
            self.initialize_user(token_decoded)
            return token_decoded
        return None

    def initialize_user(self, token_decoded: dict[str, str]):
        with SessionLocal() as session:
            username: str = get_username(token_decoded)
            if not (users_crud.get_user_by_name(session, username)):
                created_user = users_crud.create_user(session, username)
                users_crud.update_last_login(session, created_user)
                events.create_user_creation_event(session, created_user)

    def validate_token(self, token: str) -> t.Optional[t.Dict[str, t.Any]]:
        try:
            jwt_cfg = ep_main.get_jwk_cfg(token)
        except Exception:
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "err_code": "TOKEN_INVALID",
                        "reason": "The used token is not valid.",
                    },
                ) from None
            return None
        try:
            return jwt.decode(token, **jwt_cfg)
        except jwt.ExpiredSignatureError:
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "err_code": "token_exp",
                        "reason": "The Signature of the token is expired. Please request a new access token.",
                    },
                ) from None
            return None
        except (jwt.JWTError, jwt.JWTClaimsError):
            if self.auto_error:
                raise HTTPException(
                    status_code=401,
                    detail={
                        "technical": "The validation of your access token failed. Please contact your administrator.",
                    },
                ) from None
            return None
