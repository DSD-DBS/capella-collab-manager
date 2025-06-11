# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.toolmodels.backups import crud as pipelines_crud
from capellacollab.projects.toolmodels.backups import (
    models as pipelines_models,
)
from capellacollab.projects.toolmodels.backups import (
    routes as pipelines_routes,
)

router = fastapi.APIRouter()
log = logging.getLogger(__name__)


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        pipelines={permissions_models.UserTokenVerb.GET}
                    )
                )
            )
        )
    ],
)
def get_all_pipelines(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> list[pipelines_models.ExtendedPipeline]:
    return [
        pipelines_routes.add_next_run_to_pipeline(
            pipelines_models.ExtendedPipeline.model_validate(pipeline)
        )
        for pipeline in pipelines_crud.get_all_pipelines(db)
    ]
