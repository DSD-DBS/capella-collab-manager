# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
import pydantic

from capellacollab.core import responses
from capellacollab.core.logging import injectables as logging_injectables
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import exceptions, injectables, models

users_router = fastapi.APIRouter()
router = fastapi.APIRouter()


@router.get("")
def get_available_permissions():
    return models.GlobalScopes.model_json_schema()


@router.get(
    "/validate",
    status_code=204,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.InvalidPermissionFormatError,
            exceptions.PermissionOrVerbNotFoundError,
        ]
    ),
)
def validate_permissions(
    required_scopes: t.Annotated[
        list[str],
        fastapi.Query(
            description=(
                "List of required scopes. A scope consists of a locator and a verb."
                " The locator is a string with comma-separated attributes in the format `group.permissions`."
                " The verb is the required verb for the given locator. "
                " The values are combined using colon in the format `group.permission:verb`."
                "<br /><br />"
            ),
            example=["admin.users:get", "admin.users:create"],
        ),
    ],
    actual_scope: t.Annotated[
        models.GlobalScopes, fastapi.Depends(injectables.get_scope)
    ],
    logger: t.Annotated[
        logging.LoggerAdapter,
        fastapi.Depends(logging_injectables.get_request_logger),
    ],
):
    """Validate permissions against required scopes"""
    merged_required_scopes = models.GlobalScopes()
    for scope in [
        _resolve_permission_from_locator_and_verb(scope, logger)
        for scope in required_scopes
    ]:
        merged_required_scopes |= scope

    injectables.PermissionValidation(required_scope=merged_required_scopes)(
        actual_scope=actual_scope
    )


def _resolve_permission_from_locator_and_verb(
    scope: str, logger: logging.LoggerAdapter
) -> models.GlobalScopes:
    """Resolve permission from attribute locator and verb.

    Resolve a string with the example format
    `admin.users:get` to the corresponding permission object:
    `{"admin": {"users": ["GET"]}}`
    """

    resolved_scope = scope.split(":")
    if len(resolved_scope) != 2:
        raise exceptions.InvalidPermissionFormatError(scope)

    attribute_locator, verb = resolved_scope

    permission: t.Any = {verb.upper()}

    for attribute in attribute_locator.split(".")[::-1]:
        permission = {attribute: permission}

    try:
        return models.GlobalScopes.model_validate(permission)
    except pydantic.ValidationError as e:
        logger.info("Permission or verb not found.", exc_info=True)
        raise exceptions.PermissionOrVerbNotFoundError(
            attribute_locator, verb
        ) from e


@users_router.get(
    "",
)
def get_actual_permissions(
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_existing_user),
    ],
    own_user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    global_scope: t.Annotated[
        models.GlobalScopes, fastapi.Depends(injectables.get_scope)
    ],
) -> models.GlobalScopes:
    """Get the actual permissions for a user.

    Can be requested for the own user
    or for another user if the requesting user has the `admin.users:get` permission.
    """

    if (
        user.id != own_user.id
        and models.UserTokenVerb.GET not in global_scope.admin.users
    ):
        raise exceptions.InsufficientPermissionError(
            "admin.users", {models.UserTokenVerb.GET}
        )

    return injectables.get_scope(user, None)
