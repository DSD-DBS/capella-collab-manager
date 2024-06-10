# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

import fastapi
from fastapi import security

from capellacollab.core import database
from capellacollab.users import crud as user_crud
from capellacollab.users.tokens import crud as token_crud

from . import exceptions

logger = logging.getLogger(__name__)


class HTTPBasicAuth(security.HTTPBasic):
    def __init__(self):
        super().__init__(auto_error=True)

    async def __call__(self, request: fastapi.Request) -> str:  # type: ignore
        credentials: security.HTTPBasicCredentials | None = (
            await super().__call__(request)
        )
        if not credentials:
            raise exceptions.UnauthenticatedError()
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
                raise exceptions.InvalidPersonalAccessTokenError()

            if db_token.expiration_date < datetime.date.today():
                logger.info("Token expired for user %s", credentials.username)
                raise exceptions.PersonalAccessTokenExpired()
        return self.get_username(credentials)

    def get_username(self, credentials: security.HTTPBasicCredentials) -> str:
        return credentials.username
