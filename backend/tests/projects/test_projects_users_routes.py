# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models


@pytest.mark.usefixtures("admin")
def test_assign_read_write_permission_when_adding_manager(
    db: orm.Session,
    client: testclient.TestClient,
    user2: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/users",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "permission": projects_users_models.ProjectUserPermission.READ.value,
            "username": user2.name,
            "reason": "",
        },
    )

    project_user = projects_users_crud.get_project_user_association(
        db, project, user2
    )

    assert response.status_code == 200
    assert project_user
    assert project_user.role == projects_users_models.ProjectUserRole.MANAGER
    assert (
        project_user.permission
        == projects_users_models.ProjectUserPermission.WRITE
    )


@pytest.mark.usefixtures("admin")
def test_assign_read_write_permission_when_changing_project_role_to_manager(
    db: orm.Session,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    user2: users_models.DatabaseUser,
):
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        projects_users_models.ProjectUserRole.USER,
        projects_users_models.ProjectUserPermission.READ,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user2.id}",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "reason": "",
        },
    )

    project_user = projects_users_crud.get_project_user_association(
        db, project, user2
    )

    assert response.status_code == 204
    assert project_user
    assert project_user.role == projects_users_models.ProjectUserRole.MANAGER
    assert (
        project_user.permission
        == projects_users_models.ProjectUserPermission.WRITE
    )


@pytest.mark.usefixtures("admin")
def test_http_exception_when_updating_permission_of_manager(
    db: orm.Session,
    client: testclient.TestClient,
    user2: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
):
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        projects_users_models.ProjectUserRole.MANAGER,
        projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user2.id}",
        json={
            "permission": projects_users_models.ProjectUserPermission.READ.value,
            "reason": "",
        },
    )

    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"]
        == "PERMISSION_FOR_PROJECT_LEADS_NOT_ALLOWED"
    )


def test_current_user_rights_for_internal_project(
    db: orm.Session,
    client: testclient.TestClient,
    executor_name: str,
    project: projects_models.DatabaseProject,
):
    projects_crud.update_project(
        db,
        project,
        projects_models.PatchProject(
            visibility=projects_models.ProjectVisibility.INTERNAL
        ),
    )
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/users/current",
    )

    assert response.status_code == 200
    assert response.json()["role"] == "user"
    assert response.json()["permission"] == "read"


def test_no_user_rights_on_internal_permissions(
    db: orm.Session,
    client: testclient.TestClient,
    executor_name: str,
    project: projects_models.DatabaseProject,
):
    projects_crud.update_project(
        db,
        project,
        projects_models.PatchProject(
            visibility=projects_models.ProjectVisibility.PRIVATE
        ),
    )
    users_crud.create_user(
        db, executor_name, executor_name, None, users_models.Role.USER
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/users/current",
    )

    assert response.status_code == 404
    assert "detail" in response.json()
    assert "reason" in response.json()["detail"]


@pytest.mark.usefixtures("admin")
def test_get_current_project_user_as_admin(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/users/current",
    )

    assert response.status_code == 200
    assert response.json()["role"] == "administrator"
    assert response.json()["permission"] == "write"


def test_get_project_users(
    db: orm.Session,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    user2: users_models.DatabaseUser,
    admin: users_models.DatabaseUser,
):
    projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=user2,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    another_user = users_crud.create_user(db, "another_user", "another_user")
    projects_users_crud.add_user_to_project(
        db,
        project=project,
        user=another_user,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get(f"/api/v1/projects/{project.slug}/users")

    assert len(response.json()) == 4
    usernames = [user["user"]["name"] for user in response.json()]

    assert admin.name in usernames
    assert user2.name in usernames
    assert another_user.name in usernames


@pytest.mark.usefixtures("admin")
def test_fail_to_add_existing_user(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    user2: users_models.DatabaseUser,
):
    """Try to add a user twice to a project"""
    response = client.post(
        f"/api/v1/projects/{project.slug}/users",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "permission": projects_users_models.ProjectUserPermission.READ.value,
            "username": user2.name,
            "reason": "",
        },
    )

    assert response.status_code == 200

    response = client.post(
        f"/api/v1/projects/{project.slug}/users",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "permission": projects_users_models.ProjectUserPermission.READ.value,
            "username": user2.name,
            "reason": "",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"] == "PROJECT_USER_ALREADY_EXISTS"
    )
