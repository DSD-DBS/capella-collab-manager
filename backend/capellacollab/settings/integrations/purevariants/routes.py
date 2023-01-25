# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import fastapi
from sqlalchemy.orm import Session

from capellacollab.core.authentication import injectables as auth_injectables
from capellacollab.core.database import get_db
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.operators.k8s import KubernetesOperator
from capellacollab.settings.integrations.purevariants import crud
from capellacollab.settings.integrations.purevariants.models import (
    DatabasePureVariantsLicenses,
    PureVariantsLicenses,
)
from capellacollab.users.models import Role

router = fastapi.APIRouter(
    dependencies=[
        fastapi.Depends(
            auth_injectables.RoleVerification(required_role=Role.ADMIN)
        )
    ],
)


@router.get(
    "",
    response_model=PureVariantsLicenses | None,
)
def get_license(
    db: Session = fastapi.Depends(get_db),
) -> DatabasePureVariantsLicenses | None:
    return crud.get_pure_variants_configuration(db)


@router.patch(
    "",
    response_model=PureVariantsLicenses,
)
def set_license(
    body: PureVariantsLicenses, db: Session = fastapi.Depends(get_db)
) -> DatabasePureVariantsLicenses:
    return crud.set_license_server_configuration(db, body.license_server_url)


@router.post(
    "/license-keys",
    response_model=PureVariantsLicenses,
)
def upload_license_key_file(
    file: fastapi.UploadFile,
    operator: KubernetesOperator = fastapi.Depends(get_operator),
    db: Session = fastapi.Depends(get_db),
):
    operator.create_secret(
        "pure-variants", {"license.lic": file.file.read()}, overwrite=True
    )
    return crud.set_license_key_filename(db, value=file.filename)


@router.delete("/license-keys/0")
def delete_license_key_file(
    operator: KubernetesOperator = fastapi.Depends(get_operator),
    db: Session = fastapi.Depends(get_db),
):
    crud.set_license_key_filename(db, None)
    operator.delete_secret("pure-variants")
