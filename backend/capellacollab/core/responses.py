# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import os
import typing as t

import fastapi
import pydantic

from capellacollab.config import config
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import models as users_models

from . import exceptions
from .authentication import exceptions as authentication_exceptions


def _construct_union(types: list[type[pydantic.BaseModel]]):
    return t.Union[tuple(types)]


def _create_pydantic_error_model(exc: exceptions.BaseError):
    return pydantic.create_model(
        exc.__class__.__name__,
        detail=(
            pydantic.create_model(
                f"{exc.__class__.__name__}Detail",
                title=(t.Literal[exc.title], exc.title),  # type: ignore
                reason=(t.Literal[exc.reason], exc.reason),  # type: ignore
                err_code=(t.Literal[exc.err_code], exc.err_code),  # type: ignore
                __base__=core_pydantic.BaseModel,
            ),
            ...,
        ),
        __base__=core_pydantic.BaseModel,
    )


def api_exceptions(
    excs: list[exceptions.BaseError] | None = None,
    include_authentication: bool = False,
    minimum_role: users_models.Role | None = None,
    minimum_project_role: projects_users_models.ProjectUserRole | None = None,
    minimum_project_permission: (
        projects_users_models.ProjectUserPermission | None
    ) = None,
):
    if os.getenv("CAPELLACOLLAB_SKIP_OPENAPI_ERROR_RESPONSES", "").lower() in (
        "1",
        "true",
        "t",
    ):
        return {}

    if excs is None:
        excs = []

    if include_authentication:
        excs += [
            authentication_exceptions.JWTInvalidToken(),
            authentication_exceptions.TokenSignatureExpired(),
            authentication_exceptions.RefreshTokenSignatureExpired(),
            authentication_exceptions.JWTValidationFailed(),
            authentication_exceptions.UnauthenticatedError(),
            authentication_exceptions.InvalidPersonalAccessTokenError(),
            authentication_exceptions.PersonalAccessTokenExpired(),
            authentication_exceptions.UnknownScheme("unknown"),
        ]

    if minimum_role:
        excs.append(
            authentication_exceptions.RequiredRoleNotMetError(minimum_role)
        )

    if minimum_project_role:
        excs.append(
            authentication_exceptions.RequiredProjectRoleNotMetError(
                minimum_project_role, project_slug="project_slug"
            )
        )
    if minimum_project_permission:
        excs.append(
            authentication_exceptions.RequiredProjectPermissionNotMetError(
                minimum_project_permission, project_slug="project_slug"
            )
        )

    return _translate_exceptions_to_openapi_schema(excs)


def _translate_exceptions_to_openapi_schema(excs: list[exceptions.BaseError]):
    grouped_by_status_code: dict[int, list[exceptions.BaseError]] = {}
    for exc in excs:
        grouped_by_status_code.setdefault(exc.status_code, []).append(exc)

    return {
        status_code: {
            "model": pydantic.create_model(
                "GroupedErrorResponses",
                root=(
                    _construct_union(
                        [_create_pydantic_error_model(exc) for exc in excs]
                    ),
                    ...,
                ),
                __base__=pydantic.RootModel,
            ),
        }
        for status_code, excs in grouped_by_status_code.items()
    }


def set_secure_cookie(
    response: fastapi.Response,
    key: str,
    value: str,
    path: str,
    expires: datetime.datetime | None = None,
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        expires=expires,
        path=path,
        samesite="strict",
        httponly=True,
        secure=config.general.scheme == "https",
        domain=config.general.host,
    )


def delete_secure_cookie(
    response: fastapi.Response, key: str, path: str
) -> None:
    response.delete_cookie(
        key=key,
        path=path,
        samesite="strict",
        httponly=True,
        secure=config.general.scheme == "https",
        domain=config.general.host,
    )


class SVGResponse(fastapi.responses.Response):
    """Custom error class for SVG responses.

    To use the class as response class, pass the following parameters
    to the fastapi route definition.

    ```python
    response_class=fastapi.responses.Response
    responses=responses.SVGResponse.responses
    ```

    Don't use SVGResponse as response_class as this will also change the
    media type for all error responses, see:
    https://github.com/tiangolo/fastapi/discussions/6799

    To return an SVG response in the route, use:

    ```python
    return responses.SVGResponse(
        content=b"<svg>...</svg>",
    )
    ```
    """

    media_type = "image/svg+xml"
    responses: dict[int | str, dict[str, t.Any]] | None = {
        200: {
            "content": {
                "image/svg+xml": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        }
    }
