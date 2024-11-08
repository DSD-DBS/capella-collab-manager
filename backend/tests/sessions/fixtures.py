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
from capellacollab.sessions.operators import k8s as k8s_operator
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


@pytest.fixture(name="session")
def fixture_session(
    db: orm.Session,
    basic_user: users_models.DatabaseUser,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
) -> sessions_models.DatabaseSession:
    session = sessions_models.DatabaseSession(
        id=str(uuid.uuid1()),
        created_at=datetime.datetime.now(),
        type=sessions_models.SessionType.PERSISTENT,
        environment={"CAPELLACOLLAB_SESSION_TOKEN": "thisisarandomtoken"},
        owner=basic_user,
        tool=tool,
        version=tool_version,
        connection_method_id=tool.config.connection.methods[0].id,
    )
    return sessions_crud.create_session(db, session)


@pytest.fixture(name="test_session")
def fixture_test_session(
    db: orm.Session,
    test_user: users_models.DatabaseUser,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
) -> sessions_models.DatabaseSession:
    session = sessions_models.DatabaseSession(
        id=str(uuid.uuid1()),
        created_at=datetime.datetime.now(),
        type=sessions_models.SessionType.PERSISTENT,
        environment={"CAPELLACOLLAB_SESSION_TOKEN": "thisisarandomtoken"},
        owner=test_user,
        tool=tool,
        version=tool_version,
        connection_method_id=tool.config.connection.methods[0].id,
    )
    return sessions_crud.create_session(db, session)


@pytest.fixture(name="mock_session_injection")
def fixture_mock_session_injection(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        sessions_injection, "get_last_seen", lambda _: "UNKNOWN"
    )
    monkeypatch.setattr(
        k8s_operator.KubernetesOperator,
        "get_session_state",
        lambda self, session_id: (
            sessions_models.SessionPreparationState.UNKNOWN,
            sessions_models.SessionState.UNKNOWN,
        ),
    )
