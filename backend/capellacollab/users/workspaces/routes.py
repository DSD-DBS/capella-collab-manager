# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database, responses
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import exceptions as users_exceptions
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, models, util

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ]
)


@router.get(
    "",
    response_model=list[models.Workspace],
)
def get_workspaces_for_user(
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> t.Sequence[models.DatabaseWorkspace]:
    return crud.get_workspaces_for_user(db=db, user=user)


@router.delete(
    "/{workspace_id}",
    status_code=204,
    responses=responses.api_exceptions(
        [
            exceptions.WorkspaceNotFound("test", 0),
            users_exceptions.UserNotFoundError("test"),
        ]
    ),
)
def delete_workspace(
    workspace: models.DatabaseWorkspace = fastapi.Depends(
        injectables.get_existing_user_workspace
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> None:
    util.delete_workspace(db, workspace)
