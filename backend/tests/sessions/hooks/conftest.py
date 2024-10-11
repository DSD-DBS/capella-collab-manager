# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import orm

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.fixture(name="configuration_hook_request")
def fixture_configuration_hook_request(
    db: orm.Session,
    user: users_models.DatabaseUser,
    capella_tool: tools_models.DatabaseTool,
    capella_tool_version: tools_models.DatabaseVersion,
) -> hooks_interface.ConfigurationHookRequest:
    class MockOperator:
        pass

    return hooks_interface.ConfigurationHookRequest(
        db=db,
        operator=MockOperator(),  # type: ignore
        user=user,
        tool=capella_tool,
        tool_version=capella_tool_version,
        session_type=sessions_models.SessionType.PERSISTENT,
        connection_method=tools_models.GuacamoleConnectionMethod(),
        provisioning=[],
        session_id="nxylxqbmfqwvswlqlcbsirvrt",
    )
