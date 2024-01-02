# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.users.models as projects_users_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


def test_get_user_by_id_admin(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    user = users_crud.create_user(db, "test_user")
    response = client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "test_user"


@pytest.mark.usefixtures("user")
def test_get_user_by_id_non_admin(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    user = users_crud.create_user(db, "test_user")
    response = client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 403


@pytest.mark.usefixtures("project_user")
def test_get_user_by_id_common_project(
    client: testclient.TestClient,
    db: orm.Session,
    project: projects_models.DatabaseProject,
):
    user2 = users_crud.create_user(db, "user2")
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get(f"/api/v1/users/{user2.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "user2"


@pytest.mark.usefixtures("user")
def test_get_no_common_projects(
    client: testclient.TestClient, db: orm.Session
):
    user2 = users_crud.create_user(db, "user2")
    response = client.get(f"/api/v1/users/{user2.id}/common-projects")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.usefixtures("project_user")
def test_get_common_projects(
    client: testclient.TestClient,
    db: orm.Session,
    project: projects_models.DatabaseProject,
):
    user2 = users_crud.create_user(db, "user2")
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        role=projects_users_models.ProjectUserRole.USER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get(f"/api/v1/users/{user2.id}/common-projects")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["slug"] == project.slug
