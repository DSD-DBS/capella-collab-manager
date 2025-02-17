# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s

from . import crud, models

router = fastapi.APIRouter(
    tags=["Integrations - PureVariants"],
)


@router.get(
    "",
    response_model=models.PureVariantsLicenses | None,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        pv_configuration={permissions_models.UserTokenVerb.GET}
                    )
                )
            ),
        )
    ],
)
def get_license(
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabasePureVariantsLicenses | None:
    return crud.get_pure_variants_configuration(db)


@router.patch(
    "",
    response_model=models.PureVariantsLicenses,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        pv_configuration={
                            permissions_models.UserTokenVerb.UPDATE
                        }
                    )
                )
            ),
        )
    ],
)
def set_license(
    body: models.PureVariantsLicenses,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabasePureVariantsLicenses:
    return crud.set_license_server_configuration(db, body.license_server_url)


@router.post(
    "/license-keys",
    response_model=models.PureVariantsLicenses,
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        pv_configuration={
                            permissions_models.UserTokenVerb.UPDATE
                        }
                    )
                )
            ),
        )
    ],
)
def upload_license_key_file(
    file: fastapi.UploadFile,
    operator: t.Annotated[
        k8s.KubernetesOperator, fastapi.Depends(operators.get_operator)
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    operator.create_secret(
        "pure-variants", {"license.lic": file.file.read()}, overwrite=True
    )
    return crud.set_license_key_filename(db, value=file.filename)


@router.delete(
    "/license-keys/0",
    dependencies=[
        fastapi.Depends(
            permissions_injectables.PermissionValidation(
                required_scope=permissions_models.GlobalScopes(
                    admin=permissions_models.AdminScopes(
                        pv_configuration={
                            permissions_models.UserTokenVerb.DELETE
                        }
                    )
                )
            ),
        )
    ],
)
def delete_license_key_file(
    operator: t.Annotated[
        k8s.KubernetesOperator, fastapi.Depends(operators.get_operator)
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    crud.set_license_key_filename(db, None)
    operator.delete_secret("pure-variants")
