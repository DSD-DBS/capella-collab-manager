# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi

from capellacollab.permissions import exceptions as permissions_exceptions
from capellacollab.permissions import injectables as permission_injectables
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import injectables, models

users_router = fastapi.APIRouter()
router = fastapi.APIRouter()


@router.get("")
def get_available_permissions():
    return models.GlobalScopes.model_json_schema()


@router.get("/validate")
async def validate_permissions(
    required_scopes: list[tuple[str, models.UserTokenVerb]],
    actual_scope: models.GlobalScopes = fastapi.Depends(injectables.get_scope),
):
    """Validate permissions against required scopes

    The list of required scopes to validate is passed via the `required_scopes` query parameter.
    A scope consists of a locator and a verb.
    The locator is a string with comma-separated attributes, e.g. 'admin.users'.
    The verb is the required verb for the given locator.
    """
    merged_required_scopes = models.GlobalScopes()
    for scope in [
        _resolve_permission_from_locator_and_verb(*scope)
        for scope in required_scopes
    ]:
        merged_required_scopes |= scope

    permission_injectables.PermissionValidation(
        required_scope=merged_required_scopes
    )(actual_scope=actual_scope)


def _resolve_permission_from_locator_and_verb(
    attribute_locator: str, verb: models.UserTokenVerb
) -> models.GlobalScopes:
    """Resolve permission from attribute locator and verb.

    Resolve a string with the example format
    `admin.users` and the verb GET to the corresponding permission object:
    `{"admin": {"users": ["GET]}}`
    """

    permission: t.Any = verb
    for attribute in attribute_locator.split(".")[::-1]:
        permission = {attribute: permission}
    return models.GlobalScopes.model_validate(permission)


@users_router.get(
    "",
)
def get_actual_permissions(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
    own_user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_own_user
    ),
    global_scope: models.GlobalScopes = fastapi.Depends(injectables.get_scope),
) -> models.GlobalScopes:
    if (
        user.id != own_user.id
        and models.UserTokenVerb.GET not in global_scope.admin.users
    ):
        raise permissions_exceptions.InsufficientPermissionError(
            "admin.users", {models.UserTokenVerb.GET}
        )
    return global_scope
