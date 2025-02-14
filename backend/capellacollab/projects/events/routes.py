# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
import fastapi_pagination
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.events import models as events_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import injectables as projects_injectables
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)

from . import crud

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=fastapi_pagination.Page[events_models.HistoryEvent],
    dependencies=[
        fastapi.Depends(
            projects_permissions_injectables.ProjectPermissionValidation(
                required_scope=projects_permissions_models.ProjectUserScopes(
                    access_log={permissions_models.UserTokenVerb.GET}
                )
            )
        )
    ],
)
def get_project_events(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    project: t.Annotated[projects_models.DatabaseProject, fastapi.Depends(
        projects_injectables.get_existing_project
    )],
) -> fastapi_pagination.Page[events_models.DatabaseUserHistoryEvent]:
    return crud.get_events_per_project_paginated(db, project)


fastapi_pagination.add_pagination(router)
