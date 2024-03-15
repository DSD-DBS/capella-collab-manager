# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import typing as t
import uuid

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import hooks as sessions_hooks
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s
from capellacollab.tools import models as tools_models
from capellacollab.users import models as users_models


class MockOperator:
    sessions: list[dict[str, t.Any]] = []

    def start_session(
        self,
        *args,
        **kwargs,
    ) -> k8s.Session:
        _id = str(uuid.uuid1())
        self.sessions.append({"id": _id})
        return k8s.Session(
            id=_id,
            host="test",
            port=1,
            created_at=datetime.datetime.now(),
        )


@pytest.fixture(autouse=True, name="kubernetes")
def fixture_kubernetes() -> t.Generator[MockOperator, None, None]:
    mock = MockOperator()
    mock.sessions.clear()

    def get_mock_operator():
        return mock

    app.dependency_overrides[operators.get_operator] = get_mock_operator
    yield mock
    del app.dependency_overrides[operators.get_operator]


@pytest.fixture(autouse=True, name="session_hook")
def fixture_session_hook(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(sessions_hooks, "REGISTER_HOOKS_AUTO_USE", {})


@pytest.mark.usefixtures("user", "session")
def test_no_session_is_spawned_when_conflicting_sessions(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
    db: orm.Session,
):
    """Test that no session is spawned when another session already exists."""
    response = client.post(
        "/api/v1/sessions",
        json={
            "tool_id": tool.id,
            "version_id": tool_version.id,
            "session_type": "persistent",
            "connection_method_id": tool.config.connection.methods[0].id,
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["err_code"] == "EXISTING_SESSION"
    assert len(sessions_crud.get_sessions(db)) == 1


@pytest.mark.usefixtures("user")
def test_request_session_with_invalid_connection_id(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
    db: orm.Session,
):
    """Test that the session creation fails with an invalid connection id"""
    response = client.post(
        "/api/v1/sessions",
        json={
            "tool_id": tool.id,
            "version_id": tool_version.id,
            "session_type": "persistent",
            "connection_method_id": "invalid",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"]["err_code"] == "CONNECTION_METHOD_UNKNOWN"
    assert len(sessions_crud.get_sessions(db)) == 0


@pytest.mark.usefixtures("user")
def test_request_session_with_provisioning(
    db: orm.Session,
    client: testclient.TestClient,
    capella_model: toolmodels_models.DatabaseToolModel,
    git_model: git_models.DatabaseGitModel,
):
    """Test that a session with provisioning is accepted"""

    response = client.post(
        "/api/v1/sessions",
        json={
            "tool_id": capella_model.tool.id,
            "version_id": capella_model.version.id,
            "session_type": "readonly",
            "connection_method_id": capella_model.tool.config.connection.methods[
                0
            ].id,
            "provisioning": [
                {
                    "project_slug": capella_model.project.slug,
                    "model_slug": capella_model.slug,
                    "git_model_id": git_model.id,
                    "revision": "main",
                    "deep_clone": False,
                }
            ],
        },
    )

    out = response.json()
    assert "id" in out

    assert response.is_success

    session = sessions_crud.get_session_by_id(db, out["id"])

    assert session
    assert session.type == sessions_models.SessionType.READONLY


def test_create_session_without_provisioning(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
    tool_version: tools_models.DatabaseVersion,
    tool: tools_models.DatabaseTool,
):
    """Create a session with persistent workspace"""

    response = client.post(
        "/api/v1/sessions",
        json={
            "tool_id": tool.id,
            "version_id": tool_version.id,
            "session_type": "persistent",
            "connection_method_id": tool.config.connection.methods[0].id,
        },
    )
    out = response.json()
    assert "id" in out
    session = sessions_crud.get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions