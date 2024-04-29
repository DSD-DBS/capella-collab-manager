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
