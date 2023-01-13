# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from datetime import datetime
from uuid import uuid1

import pytest

import capellacollab.sessions.guacamole
from capellacollab.__main__ import app
from capellacollab.projects.crud import create_project
from capellacollab.projects.toolmodels.crud import create_new_model
from capellacollab.projects.toolmodels.models import PostCapellaModel
from capellacollab.projects.toolmodels.modelsources.git.crud import (
    add_gitmodel_to_capellamodel,
)
from capellacollab.projects.toolmodels.modelsources.git.models import (
    PostGitModel,
)
from capellacollab.projects.users.crud import add_user_to_project
from capellacollab.projects.users.models import (
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.sessions.crud import (
    create_session,
    get_session_by_id,
    get_sessions_for_user,
)
from capellacollab.sessions.models import DatabaseSession
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.schema import WorkspaceType
from capellacollab.tools.crud import (
    create_tool,
    create_version,
    get_natures,
    get_versions,
)
from capellacollab.tools.models import Tool
from capellacollab.users.crud import create_user
from capellacollab.users.injectables import get_own_user
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
        tool_name: str,
        version_name: str,
        password: str,
        docker_image: str,
        t4c_license_secret: str | None,
        t4c_json: list[dict[str, str | int]] | None,
        pure_variants_license_server: str = None,
        pure_variants_secret_name: str = None,
    ) -> t.Dict[str, t.Any]:
        assert docker_image
        cls.sessions.append({"docker_image": docker_image})
        return {
            "id": str(uuid1()),
            "host": "test",
            "ports": [1],
            "created_at": datetime.now(),
        }

    @classmethod
    def start_readonly_session(
        cls,
        username: str,
        tool_name: str,
        version_name: str,
        password: str,
        docker_image: str,
        git_repos_json: t.List[t.Dict[str, str | int]],
    ) -> t.Dict[str, t.Any]:
        cls.sessions.append(
            {"docker_image": docker_image, "git_repos_json": git_repos_json}
        )
        return {
            "id": str(uuid1()),
            "host": "test",
            "ports": [1],
            "created_at": datetime.now(),
        }

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


@pytest.fixture()
def user(db, executor_name):
    user = create_user(db, executor_name, Role.USER)

    def get_mock_own_user():
        return user

    app.dependency_overrides[get_own_user] = get_mock_own_user
    yield user
    del app.dependency_overrides[get_own_user]


def test_get_sessions_not_authenticated(client):
    response = client.get("/api/v1/sessions")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_readonly_session_as_user(client, db, user, kubernetes):
    tool, version = next(
        (v.tool, v)
        for v in get_versions(db)
        if v.tool.name == "Capella" and v.name == "5.0.0"
    )

    model, git_model = setup_git_model_for_user(db, user, version)

    response = client.post(
        f"/api/v1/projects/{model.project.slug}/sessions/readonly",
        json={
            "models": [
                {
                    "model_slug": model.slug,
                    "git_model_id": git_model.id,
                    "revision": "main",
                    "deep_clone": False,
                }
            ]
        },
    )

    assert response.status_code == 200

    out = response.json()
    session = get_session_by_id(db, out["id"])

    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions
    assert (
        kubernetes.sessions[0]["docker_image"]
        == "k3d-myregistry.localhost:12345/capella/readonly:5.0.0-latest"
    )
    assert (
        kubernetes.sessions[0]["git_repos_json"][0]["url"]
        == model.git_models[0].path
    )


def test_no_readonly_session_as_user(client, db, user, kubernetes):
    tool = create_tool(db, Tool(name="Test"))
    version = create_version(db, tool.id, "test")

    model, git_model = setup_git_model_for_user(db, user, version)

    response = client.post(
        f"/api/v1/projects/{model.project.slug}/sessions/readonly",
        json={
            "models": [
                {
                    "model_slug": model.slug,
                    "git_model_id": git_model.id,
                    "revision": "main",
                    "deep_clone": False,
                }
            ]
        },
    )

    assert response.status_code == 409

    sessions = get_sessions_for_user(db, user.name)

    assert not sessions
    assert not kubernetes.sessions


def test_create_readonly_session_as_user(client, db, user, kubernetes):
    _tool, version = next(
        (v.tool, v)
        for v in get_versions(db)
        if v.tool.name == "Capella" and v.name == "5.0.0"
    )

    model, git_model = setup_git_model_for_user(db, user, version)
    setup_active_readonly_session(db, user, model.project, version)

    response = client.post(
        f"/api/v1/projects/{model.project.slug}/sessions/readonly",
        json={
            "models": [
                {
                    "model_slug": model.slug,
                    "git_model_id": git_model.id,
                    "revision": "main",
                    "deep_clone": False,
                }
            ]
        },
    )

    assert response.status_code == 409
    assert not kubernetes.sessions


def setup_git_model_for_user(db, user, version):
    project = create_project(db, name=str(uuid1()))
    nature = get_natures(db)[0]
    add_user_to_project(
        db,
        project,
        user,
        ProjectUserRole.USER,
        ProjectUserPermission.READ,
    )
    model = create_new_model(
        db,
        project,
        PostCapellaModel(
            name=str(uuid1()), description="", tool_id=version.tool.id
        ),
        tool=version.tool,
        version=version,
        nature=nature,
    )
    git_path = str(uuid1())
    git_model = add_gitmodel_to_capellamodel(
        db,
        model,
        PostGitModel(
            path=git_path, entrypoint="", revision="", username="", password=""
        ),
    )
    return model, git_model


def setup_active_readonly_session(db, user, project, version):
    database_model = DatabaseSession(
        id=str(uuid1()),
        type=WorkspaceType.READONLY,
        owner=user,
        project=project,
        tool=version.tool,
        version=version,
    )
    return create_session(db=db, session=database_model)


def test_create_persistent_session_as_user(client, db, user, kubernetes):
    tool, version = next(
        (v.tool, v)
        for v in get_versions(db)
        if v.tool.name == "Capella" and v.name == "5.0.0"
    )

    response = client.post(
        "/api/v1/sessions/persistent",
        json={
            "tool_id": tool.id,
            "version_id": version.id,
        },
    )
    out = response.json()
    session = get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions
    assert (
        kubernetes.sessions[0]["docker_image"]
        == "k3d-myregistry.localhost:12345/t4c/client/remote:5.0.0-latest"
    )
