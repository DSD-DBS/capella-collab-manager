# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import uuid

import pytest
from sqlalchemy import orm

from capellacollab import __main__
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import injection as sessions_injection
from capellacollab.sessions import models as sessions_models
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.fixture(name="session")
def fixture_session(
    db: orm.Session,
    user: users_models.DatabaseUser,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
) -> sessions_models.DatabaseSession:
    session = sessions_models.DatabaseSession(
        str(uuid.uuid1()),
        created_at=datetime.datetime.now(),
        type=sessions_models.SessionType.PERSISTENT,
        environment={"CAPELLACOLLAB_SESSION_TOKEN": "thisisarandomtoken"},
        owner=user,
        tool=tool,
        version=tool_version,
        connection_method_id=tool.config.connection.methods[0].id,
    )
    return sessions_crud.create_session(db, session)


@pytest.fixture(name="mock_session_injection", autouse=True)
def fixture_mock_session_injection(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        sessions_injection, "get_last_seen", lambda _: "UNKNOWN"
    )
    monkeypatch.setattr(
        sessions_injection, "determine_session_state", lambda _: "UNKNOWN"
    )
