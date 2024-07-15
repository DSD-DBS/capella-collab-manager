# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi

from capellacollab.core import database
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, models


def get_existing_user_workspace(
    workspace_id: int,
    user: users_models.DatabaseUser = fastapi.Depends(
        users_injectables.get_existing_user
    ),
    db=fastapi.Depends(database.get_db),
) -> models.DatabaseWorkspace:
    if workspace := crud.get_workspace_by_id_and_user(db, user, workspace_id):
        return workspace

    raise exceptions.WorkspaceNotFound(
        username=user.name, workspace_id=workspace_id
    )
