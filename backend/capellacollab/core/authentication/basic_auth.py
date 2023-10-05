# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

import fastapi
from fastapi import security, status

from capellacollab.core import database
from capellacollab.users import crud as user_crud
from capellacollab.users.tokens import crud as token_crud

logger = logging.getLogger(__name__)


class HTTPBasicAuth(security.HTTPBasic):
    async def __call__(  # type: ignore
        self, request: fastapi.Request
    ) -> str | None:
        credentials: security.HTTPBasicCredentials | None = (
            await super().__call__(request)
        )
        if not credentials:
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer, Basic"},
                )
            return None
        with database.SessionLocal() as session:
            user = user_crud.get_user_by_name(session, credentials.username)
            db_token = (
                token_crud.get_token_by_token_and_user(
                    session, credentials.password, user.id
                )
                if user
                else None
            )
            if not db_token:
                logger.info("Token invalid for user %s", credentials.username)
                if self.auto_error:
                    raise fastapi.HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={
                            "err_code": "BASIC_TOKEN_INVALID",
                            "reason": "The used token is not valid.",
                        },
                        headers={"WWW-Authenticate": "Bearer, Basic"},
                    )
                return None

            if db_token.expiration_date < datetime.date.today():
                logger.info("Token expired for user %s", credentials.username)
                if self.auto_error:
                    raise fastapi.HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail={
                            "err_code": "token_exp",
                            "reason": "The Signature of the token is expired. Please request a new access token.",
                        },
                        headers={"WWW-Authenticate": "Bearer, Basic"},
                    )
                return None
        return self.get_username(credentials)

    def get_username(self, credentials: security.HTTPBasicCredentials) -> str:
        return credentials.username
