# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.permissions import exceptions as permissions_exceptions
from capellacollab.permissions import models as permissions_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import injectables, models

users_router = fastapi.APIRouter()
router_without_authentication = fastapi.APIRouter()


@router_without_authentication.get("")
def get_available_permissions():
    return models.GlobalScopes.model_json_schema()


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
        and permissions_models.UserTokenVerb.GET
        not in global_scope.admin.users
    ):
        raise permissions_exceptions.InsufficientPermissionError(
            "admin.users", {permissions_models.UserTokenVerb.GET}
        )
    return global_scope
