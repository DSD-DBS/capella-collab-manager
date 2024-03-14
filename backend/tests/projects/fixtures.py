# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import pytest
from sqlalchemy import orm

from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models


@pytest.fixture(name="project")
def fixture_project(db: orm.Session) -> projects_models.DatabaseProject:
    return projects_crud.create_project(db, str(uuid.uuid1()))
