# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.settings.modelsources.t4c import crud as t4c_crud
from capellacollab.settings.modelsources.t4c import models as t4c_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="test_tool_version")
def fixture_test_tool_version(db: orm.Session) -> tools_models.DatabaseVersion:
    tool = tools_crud.create_tool_with_name(db, "Test")
    return tools_crud.create_version(db, tool, "test")


@pytest.fixture(name="admin_user")
def fixture_admin_user(
    db: orm.Session, executor_name: str
) -> users_models.DatabaseUser:
    return users_crud.create_user(db, executor_name, users_models.Role.ADMIN)


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
