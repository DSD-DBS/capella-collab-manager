# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from uuid import uuid1

from capellacollab.projects.crud import create_project
from capellacollab.projects.users.crud import add_user_to_repository
from capellacollab.projects.users.models import (
    RepositoryUserPermission,
    RepositoryUserRole,
)
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


def test_get_projects_not_authenticated(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_projects_as_user(client, db, username):
    create_user(db, username, Role.USER)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == []


def test_get_projects_as_user_with_project(client, db, username):
    project_name = str(uuid1())
    create_user(db, username, Role.USER)
    create_project(db, name=project_name)
    add_user_to_repository(
        db,
        projects_name=project_name,
        role=RepositoryUserRole.MANAGER,
        username=username,
        permission=RepositoryUserPermission.WRITE,
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": project_name,
            "slug": project_name,
            "description": None,
            "users": {"leads": 1, "contributors": 0, "subscribers": 0},
        }
    ]


def test_get_projects_as_admin(client, db, username):
    create_user(db, username, Role.ADMIN)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert {
        "name": "default",
        "slug": "default",
        "description": None,
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()
