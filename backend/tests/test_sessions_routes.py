# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from datetime import datetime
from uuid import uuid1

import pytest

import capellacollab.sessions.guacamole
from capellacollab.__main__ import app
from capellacollab.sessions.database import get_session_by_id
from capellacollab.sessions.operators import get_operator
from capellacollab.tools.crud import get_versions
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


@pytest.fixture(autouse=True)
def guacamole(monkeypatch):
    def get_admin_token() -> str:
        return "test"

    def create_user(
        token: str,
        username: str = "",
        password: str = "",
    ) -> None:
        return

    def create_connection(
        token: str,
        rdp_password: str,
        rdp_host: str,
        rdp_port: int,
    ):
        return {"identifier": "test"}

    def assign_user_to_connection(
        token: str, username: str, connection_id: str
    ):
        return

    monkeypatch.setattr(
        capellacollab.sessions.guacamole, "get_admin_token", get_admin_token
    )
    monkeypatch.setattr(
        capellacollab.sessions.guacamole, "create_user", create_user
    )
    monkeypatch.setattr(
        capellacollab.sessions.guacamole,
        "create_connection",
        create_connection,
    )
    monkeypatch.setattr(
        capellacollab.sessions.guacamole,
        "assign_user_to_connection",
        assign_user_to_connection,
    )


class MockOperator:

    sessions = []

    @classmethod
    def start_persistent_session(
        cls,
        username: str,
        password: str,
        docker_image: str,
        t4c_license_secret: str | None,
        t4c_json: list[dict[str, str | int]] | None,
    ) -> t.Dict[str, t.Any]:
        cls.sessions.append({"docker_image": docker_image})
        return {
            "id": str(uuid1()),
            "host": "test",
            "ports": [1],
            "created_at": datetime.now(),
        }

    @classmethod
    def start_readonly_session(
        self,
        password: str,
        git_url: str,
        git_revision: str,
        entrypoint: str,
        git_username: str,
        git_password: str,
    ) -> t.Dict[str, t.Any]:
        return {}

    @classmethod
    def get_session_state(self, id: str) -> str:
        return ""

    @classmethod
    def kill_session(self, id: str) -> None:
        pass

    @classmethod
    def get_session_logs(self, id: str) -> str:
        return ""

    @classmethod
    def create_cronjob(
        self, image: str, environment: t.Dict[str, str], schedule="* * * * *"
    ) -> str:
        return ""

    @classmethod
    def delete_cronjob(self, id: str) -> None:
        return None

    @classmethod
    def get_cronjob_last_run(self, id: str) -> str:
        return ""

    @classmethod
    def get_cronjob_last_state(self, name: str) -> str:
        return ""

    @classmethod
    def get_cronjob_last_starting_date(self, name: str) -> datetime | None:
        return None

    @classmethod
    def get_job_logs(self, id: str) -> str:
        return ""

    @classmethod
    def trigger_cronjob(self, name: str) -> None:
        pass


@pytest.fixture(autouse=True)
def kubernetes():
    mock = MockOperator()
    mock.sessions.clear()

    def get_mock_operator():
        return mock

    app.dependency_overrides[get_operator] = get_mock_operator
    yield mock
    del app.dependency_overrides[get_operator]


def test_get_sessions_not_authenticated(client):
    response = client.get("/api/v1/sessions")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.xfail()
def test_create_readonly_session_as_user(client, db, username):
    create_user(db, username, Role.USER)

    response = client.post(
        "/api/v1/sessions/",
        json={
            "type": "readonly",
            "branch": "main",
            "depth": "CompleteHistory",
            "repository": "myrepo",
        },
    )

    assert response.status_code == 200
    assert "id" in response.json()


def test_create_persistent_session_as_user(client, db, username, kubernetes):
    create_user(db, username, Role.USER)
    versions = get_versions(db)

    tool_id, version_id = next(
        (v.tool_id, v.id)
        for v in versions
        if v.tool.name == "Capella" and v.name == "5.0.0"
    )

    response = client.post(
        "/api/v1/sessions/persistent",
        json={
            "tool_id": tool_id,
            "version_id": version_id,
        },
    )

    out = response.json()

    session = get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == username
    assert kubernetes.sessions
    assert (
        kubernetes.sessions[0]["docker_image"]
        == "k3d-myregistry.localhost:12345/t4c/client/remote:5.0.0-latest"
    )
