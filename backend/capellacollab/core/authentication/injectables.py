# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import asyncer
import fastapi
from fastapi.security import utils as security_utils
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import api_key_cookie, basic_auth
from capellacollab.core.logging import injectables as logging_injectables
from capellacollab.users import crud as users_crud
from capellacollab.users import exceptions as users_exceptions
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models

from . import exceptions


class _AuthenticationInformationValidation:
    exceptions = [
        exceptions.JWTInvalidToken(),
        exceptions.TokenSignatureExpired(),
        exceptions.RefreshTokenSignatureExpired(),
        exceptions.JWTValidationFailed(),
        exceptions.UnauthenticatedError(),
        exceptions.InvalidPersonalAccessTokenError(),
        exceptions.PersonalAccessTokenExpired(),
        exceptions.UnknownScheme("unknown"),
    ]

    @classmethod
    async def __call__(
        cls,
        request: fastapi.Request,
        db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
        logger: t.Annotated[
            logging.LoggerAdapter,
            fastapi.Depends(logging_injectables.get_request_logger),
        ],
    ) -> tuple[
        users_models.DatabaseUser, tokens_models.DatabaseUserToken | None
    ]:
        if request.cookies.get("id_token"):
            username = await api_key_cookie.JWTAPIKeyCookie()(request)
            user = await asyncer.asyncify(users_crud.get_user_by_name)(
                db, username
            )
            if not user:
                raise users_exceptions.UserNotFoundError(username)
            return user, None

        authorization = request.headers.get("Authorization")
        scheme, _ = security_utils.get_authorization_scheme_param(
            authorization
        )

        match scheme.lower():
            case "basic":
                return await basic_auth.HTTPBasicAuth().validate(
                    db, request, logger
                )
            case "":
                raise exceptions.UnauthenticatedError()
            case _:
                raise exceptions.UnknownScheme(scheme)


authentication_information_validation = _AuthenticationInformationValidation()


def get_auth_pat(
    authentication_information: t.Annotated[
        tuple[
            users_models.DatabaseUser, tokens_models.DatabaseUserToken | None
        ],
        fastapi.Depends(authentication_information_validation),
    ],
) -> tokens_models.DatabaseUserToken | None:
    _, token = authentication_information
    return token
