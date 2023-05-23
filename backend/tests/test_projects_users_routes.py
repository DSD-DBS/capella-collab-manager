# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from capellacollab.projects.users.crud import (
    add_user_to_project,
    get_project_user_association,
)
from capellacollab.projects.users.models import (
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.users.crud import create_user
from capellacollab.users.models import Role


def test_assign_read_write_permission_when_adding_manager(
    db, client, executor_name, unique_username, project
):
    create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    response = client.post(
        f"/api/v1/projects/{project.slug}/users/",
        json={
            "role": ProjectUserRole.MANAGER.value,
            "permission": ProjectUserPermission.READ.value,
            "username": user.name,
            "reason": "",
        },
    )

    project_user = get_project_user_association(db, project, user)

    assert response.status_code == 200
    assert project_user
    assert project_user.role == ProjectUserRole.MANAGER
    assert project_user.permission == ProjectUserPermission.WRITE


def test_assign_read_write_permission_when_changing_project_role_to_manager(
    db, client, executor_name, unique_username, project
):
    create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    add_user_to_project(
        db, project, user, ProjectUserRole.USER, ProjectUserPermission.READ
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user.id}",
        json={
            "role": ProjectUserRole.MANAGER.value,
            "reason": "",
        },
    )

    project_user = get_project_user_association(db, project, user)

    assert response.status_code == 204
    assert project_user
    assert project_user.role == ProjectUserRole.MANAGER
    assert project_user.permission == ProjectUserPermission.WRITE


def test_http_exception_when_updating_permission_of_manager(
    db, client, executor_name, unique_username, project
):
    create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    add_user_to_project(
        db, project, user, ProjectUserRole.MANAGER, ProjectUserPermission.WRITE
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user.id}",
        json={
            "permission": ProjectUserPermission.READ.value,
            "reason": "",
        },
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": {
            "reason": "You are not allowed to set the permission of project leads!"
        }
    }
