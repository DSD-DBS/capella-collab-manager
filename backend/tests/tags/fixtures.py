# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.tags import crud as tags_crud
from capellacollab.tags import models as tags_models


@pytest.fixture(name="tag")
def fixture_tag(db: orm.Session) -> tags_models.DatabaseTag:
    return tags_crud.create_tag(
        db,
        tags_models.CreateTag(
            name="Pytest Tag",
            description="This badge was created by pytest",
            hex_color="#FF5733",
            icon="check",
        ),
    )
