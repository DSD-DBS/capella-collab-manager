# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

import capellacollab.settings.modelsources.t4c.repositories.crud as t4c_repositories_crud
import capellacollab.settings.modelsources.t4c.repositories.models as t4c_repositories_models
from capellacollab.settings.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.tools import models as tools_models


@pytest.fixture(name="t4c_instance")
def fixture_t4c_instance(
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
) -> t4c_models.DatabaseT4CInstance:
    server = t4c_models.DatabaseT4CInstance(
        name="test server",
        license="lic",
        host="localhost",
        usage_api="http://localhost:8086",
        rest_api="http://localhost:8080/api/v1.0",
        username="user",
        password="pass",
        protocol=t4c_models.Protocol.tcp,
        version=tool_version,
    )

    return t4c_crud.create_t4c_instance(db, server)


@pytest.fixture(name="t4c_repository")
def fixture_t4c_repository(
    t4c_instance: t4c_models.DatabaseT4CInstance,
    db: orm.Session,
) -> t4c_repositories_models.DatabaseT4CRepository:
    return t4c_repositories_crud.create_t4c_repository(
        db=db, repo_name="test", instance=t4c_instance
    )
