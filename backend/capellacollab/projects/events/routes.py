# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import fastapi_pagination
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.events import models as events_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import models as projects_users_models

from . import crud

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.ProjectRoleVerification(
                required_role=projects_users_models.ProjectUserRole.MANAGER
            )
        )
    ]
)


@router.get(
    "",
    response_model=fastapi_pagination.Page[events_models.HistoryEvent],
)
def get_events(
    db: orm.Session = fastapi.Depends(database.get_db),
    project: projects_models.DatabaseProject = fastapi.Depends(
        projects_injectables.get_existing_project
    ),
) -> fastapi_pagination.Page[events_models.DatabaseUserHistoryEvent]:
    return crud.get_events_per_project_paginated(db, project)


fastapi_pagination.add_pagination(router)
