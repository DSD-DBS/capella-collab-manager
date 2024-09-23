# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.users import models as users_models

from . import crud, exceptions, injectables, interface, models

admin_router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
)

router = fastapi.APIRouter()


@admin_router.get("", response_model=list[models.T4CLicenseServer])
def get_t4c_license_servers(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> abc.Sequence[models.DatabaseT4CLicenseServer]:
    return crud.get_t4c_license_servers(db)


@admin_router.get(
    "/{t4c_license_server_id}",
    response_model=models.T4CLicenseServer,
)
def get_t4c_license_server(
    license_server: models.DatabaseT4CLicenseServer = fastapi.Depends(
        injectables.get_existing_license_server
    ),
) -> models.DatabaseT4CLicenseServer:
    return license_server


@admin_router.post(
    "",
    response_model=models.T4CLicenseServer,
)
def create_t4c_license_server(
    body: models.T4CLicenseServerBase,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseT4CLicenseServer:
    if crud.get_t4c_license_server_by_name(db, body.name):
        raise exceptions.T4CLicenseServerWithNameAlreadyExistsError()

    body_dump = body.model_dump()

    license_server = models.DatabaseT4CLicenseServer(**body_dump)
    return crud.create_t4c_license_server(db, license_server)


@admin_router.patch(
    "/{t4c_license_server_id}",
    response_model=models.T4CLicenseServer,
)
def edit_t4c_license_server(
    body: models.PatchT4CLicenseServer,
    license_server: models.DatabaseT4CLicenseServer = fastapi.Depends(
        injectables.get_existing_license_server
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseT4CLicenseServer:
    if (
        body.name
        and body.name != license_server.name
        and crud.get_t4c_license_server_by_name(db, body.name)
    ):
        raise exceptions.T4CLicenseServerWithNameAlreadyExistsError()

    return crud.update_t4c_license_server(db, license_server, body)


@admin_router.delete(
    "/{t4c_license_server_id}",
    status_code=204,
)
def delete_t4c_license_server(
    license_server: models.DatabaseT4CLicenseServer = fastapi.Depends(
        injectables.get_existing_license_server
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    crud.delete_t4c_license_server(db, license_server)


@router.get(
    "/{t4c_license_server_id}/usage",
    response_model=interface.T4CLicenseServerUsage,
)
def fetch_t4c_license_server_licenses(
    license_server: models.DatabaseT4CLicenseServer = fastapi.Depends(
        injectables.get_existing_license_server
    ),
) -> interface.T4CLicenseServerUsage:
    return interface.get_t4c_license_server_usage(license_server.usage_api)
