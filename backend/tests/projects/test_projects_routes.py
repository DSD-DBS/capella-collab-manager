# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from unittest import mock

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.crud as projects_crud
import capellacollab.projects.models as projects_models
import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
import capellacollab.users.crud as users_crud
import capellacollab.users.models as users_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import (
    models as pipelines_models,
)


def test_get_internal_default_project_as_user(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )

    response = client.get("/api/v1/projects/melody-model-test")

    assert response.status_code == 200
    assert response.json()["name"] == "Melody Model Test"
    assert response.json()["visibility"] == "internal"
    assert response.json()["slug"] == "melody-model-test"


def test_get_projects_as_user_only_shows_default_internal_project(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    for project in data:
        assert project["visibility"] == "internal"


@pytest.mark.usefixtures("project_manager")
def test_get_projects_as_user_with_project(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
):
    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[0]["slug"] == project.slug
    assert data[0]["visibility"] == "private"


def test_get_projects_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.PRIVATE,
    )
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "private"


def test_get_internal_projects_as_user(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.INTERNAL,
    )
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "internal"


def test_get_internal_projects_as_user_without_duplicates(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    user = users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.INTERNAL,
    )
    projects_users_crud.add_user_to_project(
        db,
        project,
        user,
        projects_users_models.ProjectUserRole.USER,
        projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 1

    assert data[0]["slug"] == "melody-model-test"
    assert data[0]["visibility"] == "internal"
    assert data[0]["users"]["contributors"] == 0

    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "internal"
    assert data[-1]["users"]["contributors"] == 1


def test_create_private_project_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == "test-project"
    assert data["visibility"] == "private"


def test_create_internal_project_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == "test-project"
    assert data["visibility"] == "internal"


def test_update_project_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )
    project = projects_crud.create_project(db, "new project")

    assert project.slug == "new-project"
    assert project.visibility == projects_models.ProjectVisibility.PRIVATE
    assert project.is_archived is False

    response = client.patch(
        "/api/v1/projects/new-project",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
            "is_archived": "true",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "test project"
    assert data["slug"] == "test-project"
    assert data["visibility"] == "internal"
    assert data["is_archived"]


@pytest.mark.parametrize(
    ("run_nightly, include_commit_history"), [(True, True)]
)
def test_delete_pipeline_called_when_archiving_project(
    client: testclient.TestClient,
    db: orm.Session,
    executor_name: str,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    pipeline: pipelines_models.DatabaseBackup,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    with (
        mock.patch(
            "capellacollab.projects.routes.backups_core.delete_pipeline",
            autospec=True,
        ) as mock_delete_pipeline,
        mock.patch(
            "capellacollab.projects.routes.backups_crud.get_pipelines_for_tool_model",
            autospec=True,
        ) as mock_get_pipelines_for_tool_model,
    ):
        mock_get_pipelines_for_tool_model.return_value = [pipeline]

        response = client.patch(
            f"/api/v1/projects/{project.slug}", json={"is_archived": "true"}
        )

        assert response.status_code == 200
        mock_get_pipelines_for_tool_model.assert_called_once_with(
            db, capella_model
        )
        mock_delete_pipeline.assert_called_once_with(
            db, pipeline, mock.ANY, True
        )


@pytest.mark.usefixtures("project_user")
def test_get_project_per_role_user(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=user")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.usefixtures("project_user")
def test_get_project_per_role_manager_as_user(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=manager")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.usefixtures("project_manager")
def test_get_project_per_role_manager(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=manager")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_project_per_role_admin(
    client: testclient.TestClient,
    executor_name: str,
    db: orm.Session,
):
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.ADMIN
    )

    response = client.get("/api/v1/projects/?minimum_role=administrator")
    assert response.status_code == 200
    assert len(response.json()) > 0
