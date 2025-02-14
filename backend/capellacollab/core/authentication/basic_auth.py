# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

import fastapi
from fastapi import security
from sqlalchemy import orm

from capellacollab.users import crud as user_crud
from capellacollab.users import models as users_models
from capellacollab.users.tokens import crud as token_crud
from capellacollab.users.tokens import models as tokens_models

from . import exceptions

logger = logging.getLogger(__name__)


class HTTPBasicAuth(security.HTTPBasic):
    def __init__(self):
        super().__init__(auto_error=True)

    async def validate(
        self, db: orm.Session, request: fastapi.Request
    ) -> tuple[users_models.DatabaseUser, tokens_models.DatabaseUserToken]:
        credentials: (
            security.HTTPBasicCredentials | None
        ) = await super().__call__(request)
        if not credentials:
            raise exceptions.UnauthenticatedError()

        user = user_crud.get_user_by_name(db, credentials.username)
        if not user:
            logger.info(
                "User with username '%s' not found.", credentials.username
            )
            raise exceptions.InvalidPersonalAccessTokenError()
        db_token = token_crud.get_token_by_token_and_user(
            db, credentials.password, user.id
        )

        if not db_token:
            logger.info("Token invalid for user %s", credentials.username)
            raise exceptions.InvalidPersonalAccessTokenError()

        if db_token.expiration_date < datetime.datetime.now(tz=datetime.UTC).date():
            logger.info("Token expired for user %s", credentials.username)
            raise exceptions.PersonalAccessTokenExpired()

        return user, db_token
