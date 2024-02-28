# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.fixture(name="test_tool_version")
def fixture_test_tool_version(db: orm.Session) -> tools_models.DatabaseVersion:
    tool = tools_crud.create_tool(db, tools_models.CreateTool(name="Test"))
    return tools_crud.create_version(
        db, tool, tools_models.CreateToolVersion(name="test")
    )


@pytest.fixture(name="admin_user")
def fixture_admin_user(
    db: orm.Session, executor_name: str
) -> users_models.DatabaseUser:
    return users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
