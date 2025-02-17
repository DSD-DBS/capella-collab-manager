# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import exceptions as permissions_exceptions
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import injectables, models

router = fastapi.APIRouter()
users_router = fastapi.APIRouter()


@router.get("")
def get_available_project_permissions():
    return models.ProjectUserScopes.model_json_schema()


@users_router.get(
    "",
)
def get_actual_project_permissions(
    user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_existing_user),
    ],
    own_user: t.Annotated[
        users_models.DatabaseUser,
        fastapi.Depends(users_injectables.get_own_user),
    ],
    global_scope: t.Annotated[
        permissions_models.GlobalScopes,
        fastapi.Depends(permissions_injectables.get_scope),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project: t.Annotated[
        projects_models.DatabaseProject,
        fastapi.Depends(projects_injectables.get_existing_project),
    ],
) -> models.ProjectUserScopes:
    """Get the actual permissions for a user in a project.

    Can be requested for the own user
    or for another user if the requesting user has the `admin.users:get` permission.
    """

    if (
        user.id != own_user.id
        and permissions_models.UserTokenVerb.GET
        not in global_scope.admin.users
    ):
        raise permissions_exceptions.InsufficientPermissionError(
            "admin.users", {permissions_models.UserTokenVerb.GET}
        )

    return injectables.get_scope(
        (user, None),
        permissions_injectables.get_scope((user, None)),
        project,
        db,
    )
