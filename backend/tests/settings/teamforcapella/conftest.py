# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
import responses
from fastapi import status
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.tools import models as tools_models


@pytest.fixture(name="t4c_instance")
def fixture_t4c_instance(
    db: orm.Session,
    test_tool_version: tools_models.DatabaseVersion,
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
        version=test_tool_version,
    )

    return t4c_crud.create_t4c_instance(db, server)


@pytest.fixture(name="mock_license_server")
def fixture_mock_license_server():
    with responses.RequestsMock() as rsps:
        rsps.get(
            "http://localhost:8086/status/json",
            status=status.HTTP_200_OK,
            json={"status": {"used": 1, "free": 19, "total": 20}},
        )
        yield rsps
