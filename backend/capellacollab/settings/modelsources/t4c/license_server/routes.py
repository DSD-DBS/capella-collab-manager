# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models

from . import crud, exceptions, injectables, interface, models

router = fastapi.APIRouter()


@router.get(
    "",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_t4c_license_servers(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
    global_scope: t.Annotated[permissions_models.GlobalScopes, fastapi.Depends(
        permissions_injectables.get_scope
    )],
) -> list[models.T4CLicenseServer]:
    """Get the list of T4C license servers.

    If requested without the `admin.t4c_servers:update` scope, the license servers will be anonymized.

    """

    license_servers = [
        models.T4CLicenseServer.model_validate(license_server)
        for license_server in crud.get_t4c_license_servers(db)
    ]

    if (
        permissions_models.UserTokenVerb.GET
        not in global_scope.admin.t4c_servers
    ):
        for license_server in license_servers:
            license_server.anonymize()

    return license_servers


@router.get(
    "/{t4c_license_server_id}",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_t4c_license_server(
    license_server: t.Annotated[models.DatabaseT4CLicenseServer, fastapi.Depends(
        injectables.get_existing_license_server
    )],
    global_scope: t.Annotated[permissions_models.GlobalScopes, fastapi.Depends(
        permissions_injectables.get_scope
    )],
) -> models.T4CLicenseServer:
    """Get a T4C license server.

    If requested without the `admin.t4c_servers:update` scope, the license server will be anonymized.
    """

    license_server_pydantic = models.T4CLicenseServer.model_validate(
        license_server
    )

    if (
        permissions_models.UserTokenVerb.GET
        not in global_scope.admin.t4c_servers
    ):
        license_server_pydantic.anonymize()

    return license_server_pydantic


@router.post(
    "",
    response_model=models.T4CLicenseServer,
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
def create_t4c_license_server(
    body: models.T4CLicenseServerBase,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseT4CLicenseServer:
    if crud.get_t4c_license_server_by_name(db, body.name):
        raise exceptions.T4CLicenseServerWithNameAlreadyExistsError()

    body_dump = body.model_dump()

    license_server = models.DatabaseT4CLicenseServer(**body_dump)
    return crud.create_t4c_license_server(db, license_server)


@router.patch(
    "/{t4c_license_server_id}",
    response_model=models.T4CLicenseServer,
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
def edit_t4c_license_server(
    body: models.PatchT4CLicenseServer,
    license_server: t.Annotated[models.DatabaseT4CLicenseServer, fastapi.Depends(
        injectables.get_existing_license_server
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseT4CLicenseServer:
    if (
        body.name
        and body.name != license_server.name
        and crud.get_t4c_license_server_by_name(db, body.name)
    ):
        raise exceptions.T4CLicenseServerWithNameAlreadyExistsError()

    return crud.update_t4c_license_server(db, license_server, body)


@router.delete(
    "/{t4c_license_server_id}",
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
def delete_t4c_license_server(
    license_server: t.Annotated[models.DatabaseT4CLicenseServer, fastapi.Depends(
        injectables.get_existing_license_server
    )],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    crud.delete_t4c_license_server(db, license_server)


@router.get(
    "/{t4c_license_server_id}/usage",
    response_model=interface.T4CLicenseServerUsage,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes()
            ),
        )
    ],
)
def get_t4c_license_server_usage(
    license_server: t.Annotated[models.DatabaseT4CLicenseServer, fastapi.Depends(
        injectables.get_existing_license_server
    )],
) -> interface.T4CLicenseServerUsage:
    return interface.get_t4c_license_server_usage(license_server.usage_api)
