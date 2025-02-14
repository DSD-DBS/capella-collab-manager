# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database, responses
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.users import exceptions as users_exceptions
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, models, util

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.Workspace],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        workspaces={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_workspaces_for_user(
    user: t.Annotated[users_models.DatabaseUser, fastapi.Depends(
        users_injectables.get_existing_user
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> t.Sequence[models.DatabaseWorkspace]:
    return crud.get_workspaces_for_user(db=db, user=user)


@router.delete(
    "/{workspace_id}",
    status_code=204,
    responses=responses.translate_exceptions_to_openapi_schema(
        [
            exceptions.WorkspaceNotFound,
            users_exceptions.UserNotFoundError,
        ]
    ),
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        workspaces={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_workspace(
    workspace: t.Annotated[models.DatabaseWorkspace, fastapi.Depends(
        injectables.get_existing_user_workspace
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> None:
    util.delete_workspace(db, workspace)
