# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from capellacollab.projects.users.crud import add_user_to_project
from capellacollab.projects.users.models import (
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


def test_get_projects_not_authenticated(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_get_projects_as_user(client, db, executor_name):
    create_user(db, executor_name, Role.USER)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == []


def test_get_projects_as_user_with_project(client, db, executor_name, project):
    user = create_user(db, executor_name, Role.USER)
    add_user_to_project(
        db,
        project=project,
        user=user,
        role=ProjectUserRole.MANAGER,
        permission=ProjectUserPermission.WRITE,
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == [
        {
            "name": project.name,
            "slug": project.slug,
            "description": None,
            "users": {"leads": 1, "contributors": 0, "subscribers": 0},
        }
    ]


def test_get_projects_as_admin(client, db, executor_name):
    create_user(db, executor_name, Role.ADMIN)

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert {
        "name": "default",
        "slug": "default",
        "description": None,
        "users": {"leads": 0, "contributors": 0, "subscribers": 0},
    } in response.json()
