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
    ) -> tuple[str | None, fastapi.HTTPException | None]:
        credentials: security.HTTPBasicCredentials | None = (
            await super().__call__(request)
        )
        if not credentials:
            error = fastapi.HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer, Basic"},
            )
            if self.auto_error:
                raise error
            return None, error
        with database.SessionLocal() as session:
            user = user_crud.get_user_by_name(session, credentials.username)
            token_data = None
            if user:
                token_data = token_crud.get_token(
                    session, credentials.password, user.id
                )
            if not token_data or not user or token_data.user_id != user.id:
                logger.error("Token invalid for user %s", credentials.username)
                error = fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "err_code": "TOKEN_INVALID",
                        "reason": "The used token is not valid.",
                    },
                    headers={"WWW-Authenticate": "Bearer, Basic"},
                )
                if self.auto_error:
                    raise error
                return None, error

            if token_data.expiration_date < datetime.date.today():
                logger.error("Token expired for user %s", credentials.username)
                error = fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "err_code": "token_exp",
                        "reason": "The Signature of the token is expired. Please request a new access token.",
                    },
                    headers={"WWW-Authenticate": "Bearer, Basic"},
                )
                if self.auto_error:
                    raise error
                return None, error
        return self.get_username(credentials), None

    def get_username(self, credentials: security.HTTPBasicCredentials) -> str:
        return credentials.model_dump()["username"]
