# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.settings.integrations.purevariants.models import (
    DatabasePureVariantsLicenses,
)


def get_license(db: Session) -> DatabasePureVariantsLicenses | None:
    return db.execute(
        select(DatabasePureVariantsLicenses)
    ).scalar_one_or_none()


def set_license(db: Session, value: str) -> DatabasePureVariantsLicenses:
    if pv_license := get_license(db):
        pv_license.value = value
    else:
        pv_license = DatabasePureVariantsLicenses(value=value)
        db.add(pv_license)
    db.commit()
    return pv_license
