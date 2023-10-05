# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.crud as projects_crud
import capellacollab.projects.models as projects_models
import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
import capellacollab.users.crud as users_crud
import capellacollab.users.models as users_models


def test_get_projects_not_authenticated(client: testclient.TestClient):
    response = client.get("/api/v1/projects")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_projects_as_user_only_shows_default_internal_project(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.USER)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert {
        "name": "default",
        "slug": "default",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()


@pytest.mark.usefixtures("project_manager")
def test_get_projects_as_user_with_project(
    client: testclient.TestClient, project: projects_models.DatabaseProject
):
    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert {
        "name": project.name,
        "slug": project.slug,
        "description": "",
        "visibility": "private",
        "users": {"leads": 1, "contributors": 0, "subscribers": 0},
    } in response.json()


def test_get_projects_as_admin(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert {
        "name": "default",
        "slug": "default",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()


def test_get_internal_projects_as_user(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.USER)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert {
        "name": "default",
        "slug": "default",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()


def test_get_internal_projects_as_user_without_duplicates(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    user = users_crud.create_user(db, executor_name, users_models.Role.USER)
    project = projects_crud.create_project(
        db, "test project", visibility=projects_models.Visibility.INTERNAL
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
    assert {
        "name": "default",
        "slug": "default",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()
    assert {
        "name": "test project",
        "slug": "test-project",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 1, "subscribers": 0},
    } in response.json()
    assert len(response.json()) == 2


def test_get_internal_default_project_as_user(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.USER)

    response = client.get("/api/v1/projects/default")

    assert response.status_code == 200
    assert {
        "name": "default",
        "slug": "default",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } == response.json()


def test_create_private_project_as_admin(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
        },
    )

    assert response.status_code == 200
    assert {
        "name": "test project",
        "slug": "test-project",
        "description": "",
        "visibility": "private",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } == response.json()


def test_create_internal_project_as_admin(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)

    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
        },
    )

    assert response.status_code == 200
    assert {
        "name": "test project",
        "slug": "test-project",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } == response.json()


def test_update_project_as_admin(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    projects_crud.create_project(db, "new project")

    response = client.patch(
        "/api/v1/projects/new-project",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
        },
    )

    assert response.status_code == 200
    assert {
        "name": "test project",
        "slug": "test-project",
        "description": "",
        "visibility": "internal",
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } == response.json()
