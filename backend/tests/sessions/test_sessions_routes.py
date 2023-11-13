# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import itertools
import json
import typing as t
from datetime import datetime
from uuid import uuid1

import pytest
from fastapi import testclient

import capellacollab.sessions.guacamole
from capellacollab.__main__ import app
from capellacollab.projects.crud import create_project
from capellacollab.projects.toolmodels.crud import create_model
from capellacollab.projects.toolmodels.models import (
    DatabaseCapellaModel,
    PostCapellaModel,
)
from capellacollab.projects.toolmodels.modelsources.git.crud import (
    add_git_model_to_capellamodel,
)
from capellacollab.projects.toolmodels.modelsources.git.models import (
    PostGitModel,
)
from capellacollab.projects.users.crud import add_user_to_project
from capellacollab.projects.users.models import (
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import routes as sessions_routes
from capellacollab.sessions.crud import (
    create_session,
    get_session_by_id,
    get_sessions_for_user,
)
from capellacollab.sessions.operators import get_operator
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import models as tools_models
from capellacollab.tools.crud import (
    create_tool,
    create_tool_with_name,
    create_version,
    get_natures,
    get_versions,
)
from capellacollab.tools.integrations.crud import update_integrations
from capellacollab.tools.integrations.models import PatchToolIntegrations
from capellacollab.tools.models import DatabaseVersion
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

    def start_session(
        self,
        image: str,
        username: str,
        session_type: str,
        tool_name: str,
        version_name: str,
        volumes: list[operators_models.Volume],
        environment: dict[str, str | None],
        ports: dict[str, int],
        persistent_workspace_claim_name: str | None = None,
        prometheus_path="/metrics",
        prometheus_port=9118,
        limits="high",
    ) -> dict[str, t.Any]:
        assert image
        self.sessions.append(
            {"docker_image": image, "environment": environment}
        )
        return {
            "id": str(uuid1()),
            "host": "test",
            "ports": [1],
            "created_at": datetime.now(),
        }

    def create_public_route(
        self,
        session_id: str,
        host: str,
        path: str,
        port: int,
        wildcard_host: bool | None = False,
    ):
        pass

    def get_session_state(self, id: str) -> str:
        return ""

    def kill_session(self, id: str) -> None:
        pass

    def create_persistent_volume(
        self, name: str, size: str, labels: dict[str, str] = None
    ):
        return


@pytest.fixture(autouse=True, name="kubernetes")
def fixture_kubernetes():
    mock = MockOperator()
    mock.sessions.clear()

    def get_mock_operator():
        return mock

    app.dependency_overrides[get_operator] = get_mock_operator
    yield mock
    del app.dependency_overrides[get_operator]


@pytest.fixture(name="user")
def fixture_user(db, executor_name):
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


def test_create_readonly_session_as_user(
    client: testclient.TestClient, db, user, kubernetes
):
    _, version = next(
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
    assert "/capella/readonly:5.0.0" in kubernetes.sessions[0]["docker_image"]
    assert (
        json.loads(kubernetes.sessions[0]["environment"]["GIT_REPOS_JSON"])[0][
            "url"
        ]
        == model.git_models[0].path
    )


def test_no_readonly_session_as_user(client, db, user, kubernetes):
    tool = create_tool_with_name(db, "Test")
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


def test_one_readonly_sessions_as_user_per_tool_version(
    client, db, user, kubernetes
):
    version = next(
        v
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
    add_user_to_project(
        db,
        project,
        user,
        ProjectUserRole.USER,
        ProjectUserPermission.READ,
    )
    return setup_model(db, project, version)


def setup_model(db, project, version):
    nature = get_natures(db)[0]
    model = create_model(
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
    git_model = add_git_model_to_capellamodel(
        db,
        model,
        PostGitModel(
            path=git_path, entrypoint="", revision="", username="", password=""
        ),
    )
    return model, git_model


def setup_active_readonly_session(db, user, project, version):
    database_model = sessions_models.DatabaseSession(
        id=str(uuid1()),
        type=sessions_models.WorkspaceType.READONLY,
        owner=user,
        project=project,
        tool=version.tool,
        version=version,
        host="test",
        ports=[1],
    )
    return create_session(db=db, session=database_model)


def test_create_persistent_session_as_user(
    client: testclient.TestClient,
    db,
    user,
    kubernetes,
):
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

    assert "/capella/remote:5.0.0" in kubernetes.sessions[0]["docker_image"]


def test_create_read_only_session_as_user(
    client: testclient.TestClient,
    db,
    user,
    kubernetes,
):
    version = next(
        v
        for v in get_versions(db)
        if v.tool.name == "Capella" and v.name == "6.0.0"
    )

    model, git_model = setup_git_model_for_user(db, user, version)

    response = client.post(
        f"/api/v1/projects/{model.project.slug}/sessions/readonly",
        json={
            "models": [
                {
                    "model_slug": model.slug,
                    "git_model_id": git_model.id,
                    "revision": "test-branch",
                    "deep_clone": False,
                }
            ]
        },
    )
    out = response.json()
    print(out)
    session = get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions

    assert "/capella/readonly:6.0.0" in kubernetes.sessions[0]["docker_image"]
    assert (
        '"revision": "test-branch"'
        in kubernetes.sessions[0]["environment"]["GIT_REPOS_JSON"]
    )


def test_create_persistent_jupyter_session(client, db, user, kubernetes):
    jupyter = create_tool(
        db,
        tools_models.DatabaseTool(
            name="jupyter",
            docker_image_template="jupyter/minimal-notebook:$version",
        ),
    )
    update_integrations(
        db, jupyter.integrations, PatchToolIntegrations(jupyter=True)
    )

    jupyter_version = create_version(
        db, name="python-3.10.8", tool_id=jupyter.id
    )

    response = client.post(
        "/api/v1/sessions/persistent",
        json={
            "tool_id": jupyter.id,
            "version_id": jupyter_version.id,
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
        == "jupyter/minimal-notebook:python-3.10.8"
    )


def test_group_models_by_tool_version():
    first_tool = DatabaseVersion(id=1)
    second_tool = DatabaseVersion(id=2)

    models = [
        DatabaseCapellaModel(
            name="first",
            version=first_tool,
        ),
        DatabaseCapellaModel(
            name="second-1",
            version=second_tool,
        ),
        DatabaseCapellaModel(
            name="second-2",
            version=second_tool,
        ),
    ]

    models_by_tool = sessions_routes.group_models_by_tool_version(models)

    assert models_by_tool == [[models[0]], [models[1], models[2]]]


def test_provision_sessions_as_user(
    client: testclient.TestClient,
    db,
    user,
    kubernetes,
):
    capella_version = next(
        v
        for v in get_versions(db)
        if v.tool.name == "Capella" and v.name == "6.0.0"
    )

    jupyter_version = next(
        v for v in get_versions(db) if v.tool.name == "Jupyter"
    )

    capella_model, _capella_git_model = setup_git_model_for_user(
        db, user, capella_version
    )
    jupyter_model, _jupyter_git_model = setup_model(
        db, capella_model.project, jupyter_version
    )

    response = client.post(
        f"/api/v1/projects/{capella_model.project.slug}/sessions/provision",
        json={
            "models": [
                {
                    "model_slug": capella_model.slug,
                },
                {
                    "model_slug": jupyter_model.slug,
                },
            ],
            "persistent_workspace": True,
        },
    )
    sessions = response.json()

    assert response.status_code == 200
    assert len(sessions) == 2
    assert "/capella/readonly:6.0.0" in kubernetes.sessions[0]["docker_image"]
    assert (
        '"revision": "main"'
        in kubernetes.sessions[0]["environment"]["GIT_REPOS_JSON"]
    )
