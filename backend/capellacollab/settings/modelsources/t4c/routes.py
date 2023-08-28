# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.projects.toolmodels import routes as toolmodels_routes
from capellacollab.sessions import models as sessions_models
from capellacollab.settings.modelsources.t4c.repositories import (
    routes as settings_t4c_repositories_routes,
)
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, interface, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)


@router.get("", response_model=list[models.T4CInstance])
def list_t4c_settings(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseT4CInstance]:
    return crud.get_t4c_instances(db)


@router.get(
    "/{t4c_instance_id}",
    response_model=models.T4CInstance,
)
def get_t4c_instance(
    instance: models.DatabaseT4CInstance = fastapi.Depends(
        injectables.get_existing_instance
    ),
) -> models.DatabaseT4CInstance:
    return instance


@router.post(
    "",
    response_model=models.T4CInstance,
)
def create_t4c_instance(
    body: models.CreateT4CInstance,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseT4CInstance:
    version = toolmodels_routes.get_version_by_id_or_raise(db, body.version_id)
    instance = models.DatabaseT4CInstance(**body.model_dump())
    instance.version = version
    return crud.create_t4c_instance(db, instance)


@router.patch(
    "/{t4c_instance_id}",
    response_model=models.T4CInstance,
)
def edit_t4c_instance(
    body: models.PatchT4CInstance,
    instance: models.DatabaseT4CInstance = fastapi.Depends(
        injectables.get_existing_instance
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseT4CInstance:
    if instance.is_archived and (body.is_archived is None or body.is_archived):
        raise exceptions.T4CInstanceIsArchivedError(instance.id)

    return crud.update_t4c_instance(db, instance, body)


@router.get(
    "/{t4c_instance_id}/licenses",
    response_model=sessions_models.GetSessionUsageResponse,
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)
def fetch_t4c_licenses(
    instance: models.DatabaseT4CInstance = fastapi.Depends(
        injectables.get_existing_instance
    ),
) -> sessions_models.GetSessionUsageResponse:
    return interface.get_t4c_status(instance)


router.include_router(
    settings_t4c_repositories_routes.router,
    prefix="/{t4c_instance_id}/repositories",
)
