# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s
from capellacollab.users import models as users_models

from . import crud, models

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(
                required_role=users_models.Role.ADMIN
            )
        )
    ],
    tags=["Integrations - PureVariants"],
)


@router.get("", response_model=models.PureVariantsLicenses | None)
def get_license(
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabasePureVariantsLicenses | None:
    return crud.get_pure_variants_configuration(db)


@router.patch(
    "",
    response_model=models.PureVariantsLicenses,
)
def set_license(
    body: models.PureVariantsLicenses,
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabasePureVariantsLicenses:
    return crud.set_license_server_configuration(db, body.license_server_url)


@router.post(
    "/license-keys",
    response_model=models.PureVariantsLicenses,
)
def upload_license_key_file(
    file: fastapi.UploadFile,
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    operator.create_secret(
        "pure-variants", {"license.lic": file.file.read()}, overwrite=True
    )
    return crud.set_license_key_filename(db, value=file.filename)


@router.delete("/license-keys/0")
def delete_license_key_file(
    operator: k8s.KubernetesOperator = fastapi.Depends(operators.get_operator),
    db: orm.Session = fastapi.Depends(database.get_db),
):
    crud.set_license_key_filename(db, None)
    operator.delete_secret("pure-variants")
