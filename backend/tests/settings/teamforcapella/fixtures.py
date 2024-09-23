# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

import capellacollab.settings.modelsources.t4c.instance.repositories.crud as t4c_repositories_crud
import capellacollab.settings.modelsources.t4c.instance.repositories.models as t4c_repositories_models
from capellacollab.settings.modelsources.t4c.instance import (
    crud as t4c_instance_crud,
)
from capellacollab.settings.modelsources.t4c.instance import (
    models as t4c_instance_models,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    crud as t4c_license_server_crud,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    models as t4c_license_server_models,
)
from capellacollab.tools import models as tools_models


@pytest.fixture(name="t4c_license_server")
def fixture_t4c_license_server(
    db: orm.Session,
) -> t4c_license_server_models.DatabaseT4CLicenseServer:
    license_server = t4c_license_server_models.DatabaseT4CLicenseServer(
        name="test license server",
        usage_api="http://localhost:8086",
        license_key="test key",
    )

    return t4c_license_server_crud.create_t4c_license_server(
        db, license_server
    )


@pytest.fixture(name="t4c_instance")
def fixture_t4c_instance(
    db: orm.Session,
    capella_tool_version: tools_models.DatabaseVersion,
    t4c_license_server: t4c_license_server_models.DatabaseT4CLicenseServer,
) -> t4c_instance_models.DatabaseT4CInstance:
    server = t4c_instance_models.DatabaseT4CInstance(
        name="test server",
        host="localhost",
        license_server=t4c_license_server,
        rest_api="http://localhost:8080/api/v1.0",
        username="user",
        password="pass",
        protocol=t4c_instance_models.Protocol.tcp,
        version=capella_tool_version,
    )

    return t4c_instance_crud.create_t4c_instance(db, server)


@pytest.fixture(name="t4c_repository")
def fixture_t4c_repository(
    t4c_instance: t4c_instance_models.DatabaseT4CInstance,
    db: orm.Session,
) -> t4c_repositories_models.DatabaseT4CRepository:
    return t4c_repositories_crud.create_t4c_repository(
        db=db, repo_name="test", instance=t4c_instance
    )
