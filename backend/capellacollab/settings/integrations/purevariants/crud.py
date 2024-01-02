# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.settings.integrations.purevariants import models


def get_pure_variants_configuration(
    db: orm.Session,
) -> models.DatabasePureVariantsLicenses | None:
    return db.execute(
        sa.select(models.DatabasePureVariantsLicenses)
    ).scalar_one_or_none()


def set_license_server_configuration(
    db: orm.Session, value: str | None
) -> models.DatabasePureVariantsLicenses:
    if pv_license := get_pure_variants_configuration(db):
        pv_license.license_server_url = value
    else:
        pv_license = models.DatabasePureVariantsLicenses(
            license_server_url=value, license_key_filename=None
        )
        db.add(pv_license)
    db.commit()
    return pv_license


def set_license_key_filename(
    db: orm.Session, value: str | None
) -> models.DatabasePureVariantsLicenses:
    if pv_license := get_pure_variants_configuration(db):
        pv_license.license_key_filename = value
    else:
        pv_license = models.DatabasePureVariantsLicenses(
            license_server_url=None, license_key_filename=value
        )
        db.add(pv_license)
    db.commit()
    return pv_license
