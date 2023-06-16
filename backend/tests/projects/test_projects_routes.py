# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as projects_models
import capellacollab.users.crud as users_crud
import capellacollab.users.models as users_models


def test_get_projects_not_authenticated(client: testclient.TestClient):
    response = client.get("/api/v1/projects")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_projects_as_user(
    client: testclient.TestClient, db: orm.Session, executor_name: str
):
    users_crud.create_user(db, executor_name, users_models.Role.USER)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.usefixtures("project_manager")
def test_get_projects_as_user_with_project(
    client: testclient.TestClient, project: projects_models.DatabaseProject
):
    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": project.name,
            "slug": project.slug,
            "description": "",
            "users": {"leads": 1, "contributors": 0, "subscribers": 0},
        }
    ]


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
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()
