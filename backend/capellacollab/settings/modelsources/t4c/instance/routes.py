# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t
from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    routes as settings_t4c_repositories_routes,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    crud as t4c_license_server_crud,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    exceptions as t4c_license_server_exceptions,
)
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import exceptions as tools_exceptions

from . import crud, exceptions, injectables, models

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[models.T4CInstance],
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_servers={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_t4c_instances(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> abc.Sequence[models.DatabaseT4CInstance]:
    return crud.get_t4c_instances(db)


@router.get(
    "/{t4c_instance_id}",
    response_model=models.T4CInstance,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_servers={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_t4c_instance(
    instance: t.Annotated[
        models.DatabaseT4CInstance,
        fastapi.Depends(injectables.get_existing_instance),
    ],
) -> models.DatabaseT4CInstance:
    return instance


@router.post(
    "",
    response_model=models.T4CInstance,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_servers={permissions_models.UserTokenVerb.CREATE}
                    )
                )
            ),
        )
    ],
)
def create_t4c_instance(
    body: models.CreateT4CInstance,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseT4CInstance:
    if crud.get_t4c_instance_by_name(db, body.name):
        raise exceptions.T4CInstanceWithNameAlreadyExistsError()

    if not (version := tools_crud.get_version_by_id(db, body.version_id)):
        raise tools_exceptions.ToolVersionNotFoundError(body.version_id)
    if not (
        license_server := t4c_license_server_crud.get_t4c_license_server_by_id(
            db, body.license_server_id
        )
    ):
        raise t4c_license_server_exceptions.T4CLicenseServerNotFoundError(
            body.license_server_id
        )

    body_dump = body.model_dump()
    del body_dump["version_id"]
    del body_dump["license_server_id"]

    instance = models.DatabaseT4CInstance(
        version=version, license_server=license_server, **body_dump
    )
    instance.version = version
    instance.license_server = license_server
    return crud.create_t4c_instance(db, instance)


@router.patch(
    "/{t4c_instance_id}",
    response_model=models.T4CInstance,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_servers={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            ),
        )
    ],
)
def edit_t4c_instance(
    body: models.PatchT4CInstance,
    instance: t.Annotated[
        models.DatabaseT4CInstance,
        fastapi.Depends(injectables.get_existing_instance),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
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


@router.delete(
    "/{t4c_instance_id}",
    status_code=204,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        t4c_servers={permissions_models.UserTokenVerb.DELETE}
                    )
                )
            ),
        )
    ],
)
def delete_t4c_instance(
    instance: t.Annotated[
        models.DatabaseT4CInstance,
        fastapi.Depends(injectables.get_existing_instance),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    crud.delete_t4c_instance(db, instance)


router.include_router(
    settings_t4c_repositories_routes.router,
    prefix="/{t4c_instance_id}/repositories",
)
