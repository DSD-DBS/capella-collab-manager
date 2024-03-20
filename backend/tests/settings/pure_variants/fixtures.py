# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.settings.integrations.purevariants import (
    crud as pure_variants_crud,
)
from capellacollab.settings.integrations.purevariants import (
    models as pure_variants_models,
)


@pytest.fixture(name="pure_variants_license")
def fixture_pure_variants_license(
    db: orm.Session,
) -> pure_variants_models.DatabasePureVariantsLicenses:
    pure_variants_crud.set_license_server_configuration(
        db, value="http://127.0.0.1:27000"
    )
    pure_variants_crud.set_license_key_filename(db, value="xy.license")
    license_configuration = pure_variants_crud.get_pure_variants_configuration(
        db
    )
    assert license_configuration
    return license_configuration
