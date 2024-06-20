# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.settings.modelsources.t4c.repositories import (
    routes as settings_t4c_repositories_routes,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import exceptions as tools_exceptions
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
def get_t4c_instances(
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
    if crud.get_t4c_instance_by_name(db, body.name):
        raise exceptions.T4CInstanceWithNameAlreadyExistsError()

    if not (version := tools_crud.get_version_by_id(db, body.version_id)):
        raise tools_exceptions.ToolVersionNotFoundError(body.version_id)
    body_dump = body.model_dump()
    del body_dump["version_id"]

    instance = models.DatabaseT4CInstance(version=version, **body_dump)
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
    if (
        body.name
        and body.name != instance.name
        and crud.get_t4c_instance_by_name(db, body.name)
    ):
        raise exceptions.T4CInstanceWithNameAlreadyExistsError()

    return crud.update_t4c_instance(db, instance, body)


@router.get(
    "/{t4c_instance_id}/licenses",
    response_model=models.GetSessionUsageResponse,
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
) -> models.GetSessionUsageResponse:
    return interface.get_t4c_status(instance)


router.include_router(
    settings_t4c_repositories_routes.router,
    prefix="/{t4c_instance_id}/repositories",
)
