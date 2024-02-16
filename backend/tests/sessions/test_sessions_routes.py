# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import json
import typing as t
from uuid import uuid1

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.sessions.guacamole
from capellacollab.__main__ import app
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.git import crud as git_crud
from capellacollab.projects.toolmodels.modelsources.git import (
    models as git_models,
)
from capellacollab.projects.users import crud as project_users_crud
from capellacollab.projects.users import models as project_users_models
from capellacollab.sessions import crud as sessions_crud
from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.operators import k8s
from capellacollab.sessions.operators import models as operators_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models
from capellacollab.tools.integrations import crud as integrations_crud
from capellacollab.tools.integrations import models as integrations_models
from capellacollab.users import crud as users_crud
from capellacollab.users import injectables as users_injectables
from capellacollab.users import models as users_models


@pytest.fixture(autouse=True)
def guacamole(monkeypatch):
    def get_admin_token() -> str:
        return "test"

    # pylint: disable=unused-argument
    def create_user(
        token: str,
        username: str = "",
        password: str = "",
    ) -> None:
        return

    # pylint: disable=unused-argument
    def create_connection(
        token: str,
        rdp_password: str,
        rdp_host: str,
        rdp_port: int,
    ):
        return {"identifier": "test"}

    # pylint: disable=unused-argument
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
    sessions: list[dict[str, t.Any]] = []

    # pylint: disable=unused-argument
    def start_session(
        self,
        image: str,
        username: str,
        session_type: str,
        tool_name: str,
        version_name: str,
        environment: dict[str, str],
        ports: dict[str, int],
        volumes: list[operators_models.Volume],
        prometheus_path="/metrics",
        prometheus_port=9118,
        limits="high",
    ) -> k8s.Session:
        assert image
        self.sessions.append(
            {"docker_image": image, "environment": environment}
        )
        return k8s.Session(
            id=str(uuid1()),
            host="test",
            ports={1},
            created_at=datetime.datetime.now(),
        )

    def create_public_route(
        self,
        session_id: str,
        host: str,
        path: str,
        port: int,
        wildcard_host: bool | None = False,
    ):
        pass

    # pylint: disable=unused-argument
    def get_session_state(self, id: str) -> str:
        return ""

    def kill_session(self, id: str) -> None:
        pass

    # pylint: disable=unused-argument
    def create_persistent_volume(
        self,
        name: str,
        size: str,
        labels: dict[str, str] | None = None,
    ):
        return


@pytest.fixture(autouse=True, name="kubernetes")
def fixture_kubernetes() -> t.Generator[MockOperator, None, None]:
    mock = MockOperator()
    mock.sessions.clear()

    def get_mock_operator():
        return mock

    app.dependency_overrides[operators.get_operator] = get_mock_operator
    yield mock
    del app.dependency_overrides[operators.get_operator]


@pytest.fixture(name="user")
def fixture_user(
    db: orm.Session, executor_name: str
) -> t.Generator[users_models.DatabaseUser, None, None]:
    user = users_crud.create_user(db, executor_name, users_models.Role.USER)

    def get_mock_own_user():
        return user

    app.dependency_overrides[users_injectables.get_own_user] = (
        get_mock_own_user
    )
    yield user
    del app.dependency_overrides[users_injectables.get_own_user]


def test_get_sessions_not_authenticated(client: testclient.TestClient):
    response = client.get("/api/v1/sessions")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_create_readonly_session_as_user(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
):
    _, version = next(
        (v.tool, v)
        for v in tools_crud.get_versions(db)
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
    session = sessions_crud.get_session_by_id(db, out["id"])

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


def test_no_readonly_session_as_user(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
):
    tool = tools_crud.create_tool_with_name(db, "Test")
    version = tools_crud.create_version(db, tool, "test")

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

    sessions = sessions_crud.get_sessions_for_user(db, user.name)

    assert not sessions
    assert not kubernetes.sessions


def test_one_readonly_sessions_as_user_per_tool_version(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
):
    version = next(
        v
        for v in tools_crud.get_versions(db)
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


def setup_git_model_for_user(
    db: orm.Session,
    user: users_models.DatabaseUser,
    version: tools_models.DatabaseVersion,
):
    project = projects_crud.create_project(db, name=str(uuid1()))
    nature = tools_crud.get_natures(db)[0]
    project_users_crud.add_user_to_project(
        db,
        project,
        user,
        project_users_models.ProjectUserRole.USER,
        project_users_models.ProjectUserPermission.READ,
    )
    model = toolmodels_crud.create_model(
        db,
        project,
        toolmodels_models.PostCapellaModel(
            name=str(uuid1()), description="", tool_id=version.tool.id
        ),
        tool=version.tool,
        version=version,
        nature=nature,
    )
    git_path = str(uuid1())
    git_model = git_crud.add_git_model_to_capellamodel(
        db,
        model,
        git_models.PostGitModel(
            path=git_path, entrypoint="", revision="", username="", password=""
        ),
    )
    return model, git_model


def setup_active_readonly_session(
    db: orm.Session,
    user: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    version: tools_models.DatabaseVersion,
):
    database_model = sessions_models.DatabaseSession(
        id=str(uuid1()),
        type=sessions_models.WorkspaceType.READONLY,
        owner=user,
        project=project,
        tool=version.tool,
        version=version,
        host="test",
        ports=[1],
        created_at=datetime.datetime.now(),
        environment={},
    )
    return sessions_crud.create_session(db=db, session=database_model)


def test_create_persistent_session_as_user(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
):
    tool, version = next(
        (v.tool, v)
        for v in tools_crud.get_versions(db)
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
    session = sessions_crud.get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions

    assert "/capella/remote:5.0.0" in kubernetes.sessions[0]["docker_image"]


def test_create_read_only_session_as_user(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
):
    version = next(
        v
        for v in tools_crud.get_versions(db)
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
    session = sessions_crud.get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions

    assert "/capella/readonly:6.0.0" in kubernetes.sessions[0]["docker_image"]
    assert (
        '"revision": "test-branch"'
        in kubernetes.sessions[0]["environment"]["GIT_REPOS_JSON"]
    )


def test_create_persistent_jupyter_session(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
    kubernetes: MockOperator,
):
    jupyter = tools_crud.create_tool(
        db,
        tools_models.DatabaseTool(
            name="jupyter",
            docker_image_template="jupyter/minimal-notebook:$version",
        ),
    )
    assert jupyter.integrations
    integrations_crud.update_integrations(
        db,
        jupyter.integrations,
        integrations_models.PatchToolIntegrations(jupyter=True),
    )

    jupyter_version = tools_crud.create_version(
        db, name="python-3.10.8", tool=jupyter
    )

    response = client.post(
        "/api/v1/sessions/persistent",
        json={
            "tool_id": jupyter.id,
            "version_id": jupyter_version.id,
        },
    )
    out = response.json()
    session = sessions_crud.get_session_by_id(db, out["id"])

    assert response.status_code == 200
    assert session
    assert session.owner_name == user.name
    assert kubernetes.sessions
    assert (
        kubernetes.sessions[0]["docker_image"]
        == "jupyter/minimal-notebook:python-3.10.8"
    )
