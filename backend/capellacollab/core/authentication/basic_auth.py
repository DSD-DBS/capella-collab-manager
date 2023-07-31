# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import fastapi
from fastapi import security, status

from capellacollab.core import database
from capellacollab.users import crud as user_crud
from capellacollab.users.tokens import crud as token_crud


class HTTPBasicAuth(security.HTTPBasic):
    async def __call__(
        self, request: fastapi.Request
    ) -> security.HTTPBasicCredentials | None:
        credentials: security.HTTPBasicCredentials | None = (
            await super().__call__(request)
        )
        if not credentials:
            if self.auto_error:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Basic"},
                )
            return None

        with database.SessionLocal() as session:
            user = user_crud.get_user_by_name(session, credentials.username)
            token_data = token_crud.get_token(session, credentials.password)
            if not token_data or not user or token_data.user_id != user.id:
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "err_code": "TOKEN_INVALID",
                        "reason": "The used token is not valid.",
                    },
                    headers={"WWW-Authenticate": "Basic"},
                )
            if token_data.expiration_date < datetime.datetime.now():
                raise fastapi.HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "err_code": "token_exp",
                        "reason": "The Signature of the token is expired. Please request a new access token.",
                    },
                )

        return credentials
