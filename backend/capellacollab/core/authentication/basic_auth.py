# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import typing as t

import argon2
import asyncer
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
        self,
        db: orm.Session,
        request: fastapi.Request,
        logger: logging.LoggerAdapter,
    ) -> tuple[users_models.DatabaseUser, tokens_models.DatabaseUserToken]:
        credentials: (
            security.HTTPBasicCredentials | None
        ) = await super().__call__(request)
        if not credentials:
            raise exceptions.UnauthenticatedError()

        user = await asyncer.asyncify(user_crud.get_user_by_name)(
            db, credentials.username
        )

        if not user:
            logger.info(
                "User with username '%s' not found.", credentials.username
            )
            raise exceptions.InvalidPersonalAccessTokenError()

        password = credentials.password.split("_")
        if len(password) == 2:
            # Legacy token
            tokens = await asyncer.asyncify(
                token_crud.get_all_tokens_for_user
            )(db, user.id)
            db_token = await asyncer.asyncify(
                self.validate_password_hash_legacy
            )(tokens, credentials.password)
            if not db_token:
                logger.info(
                    "Token not valid for user %s", credentials.username
                )
                raise exceptions.InvalidPersonalAccessTokenError()
        elif len(password) == 3:
            token_id = int(password[2])
            db_token = await asyncer.asyncify(
                token_crud.get_token_by_id_and_user
            )(db, token_id, user)

            if not db_token:
                logger.info(
                    "Token not found for user %s", credentials.username
                )
                raise exceptions.InvalidPersonalAccessTokenError()

            await asyncer.asyncify(self.validate_password_hash)(
                db_token, password[1]
            )
        else:
            logger.info(
                "Token has invalid structure, resolved length is %d",
                len(password),
            )
            raise exceptions.InvalidPersonalAccessTokenError()

        if (
            db_token.expiration_date
            < datetime.datetime.now(tz=datetime.UTC).date()
        ):
            logger.info("Token expired for user %s", credentials.username)
            raise exceptions.PersonalAccessTokenExpired()

        return user, db_token

    @classmethod
    def validate_password_hash(
        cls, token: tokens_models.DatabaseUserToken, password: str
    ):
        ph = argon2.PasswordHasher(
            time_cost=1, memory_cost=2048, parallelism=1
        )

        try:
            ph.verify(token.hash, password)
        except argon2.exceptions.VerifyMismatchError as e:
            raise exceptions.InvalidPersonalAccessTokenError() from e

    @classmethod
    def validate_password_hash_legacy(
        cls, tokens: t.Sequence[tokens_models.DatabaseUserToken], password: str
    ):
        ph = argon2.PasswordHasher(
            time_cost=1, memory_cost=2048, parallelism=1
        )

        for token in tokens:
            try:
                ph.verify(token.hash, password)
                return token
            except argon2.exceptions.VerifyMismatchError:
                pass
        return None
