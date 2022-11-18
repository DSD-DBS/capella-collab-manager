# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from capellacollab.core.authentication.database import RoleVerification
from capellacollab.core.database import get_db
from capellacollab.settings.integrations.purevariants import crud
from capellacollab.settings.integrations.purevariants.models import (
    DatabasePureVariantsLicenses,
    PureVariantsLicenses,
)
from capellacollab.users.models import Role

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
    response_model=t.Optional[PureVariantsLicenses],
)
def get_license(
    db: Session = Depends(get_db),
) -> DatabasePureVariantsLicenses | None:
    return crud.get_license(db)


@router.patch(
    "/",
    dependencies=[Depends(RoleVerification(required_role=Role.ADMIN))],
    response_model=PureVariantsLicenses,
)
def set_license(
    body: PureVariantsLicenses, db: Session = Depends(get_db)
) -> DatabasePureVariantsLicenses:
    return crud.set_license(db, body.value)
