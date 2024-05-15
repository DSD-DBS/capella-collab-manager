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


def test_assign_read_write_permission_when_adding_manager(
    db: orm.Session,
    client: testclient.TestClient,
    executor_name: str,
    unique_username: str,
    project: projects_models.DatabaseProject,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    user = users_crud.create_user(db, unique_username, users_models.Role.USER)

    response = client.post(
        f"/api/v1/projects/{project.slug}/users/",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "permission": projects_users_models.ProjectUserPermission.READ.value,
            "username": user.name,
            "reason": "",
        },
    )

    project_user = projects_users_crud.get_project_user_association(
        db, project, user
    )

    assert response.status_code == 200
    assert project_user
    assert project_user.role == projects_users_models.ProjectUserRole.MANAGER
    assert (
        project_user.permission
        == projects_users_models.ProjectUserPermission.WRITE
    )


def test_assign_read_write_permission_when_changing_project_role_to_manager(
    db: orm.Session,
    client: testclient.TestClient,
    executor_name: str,
    unique_username: str,
    project: projects_models.DatabaseProject,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    user = users_crud.create_user(db, unique_username, users_models.Role.USER)

    projects_users_crud.add_user_to_project(
        db,
        project,
        user,
        projects_users_models.ProjectUserRole.USER,
        projects_users_models.ProjectUserPermission.READ,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user.id}",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "reason": "",
        },
    )

    project_user = projects_users_crud.get_project_user_association(
        db, project, user
    )

    assert response.status_code == 204
    assert project_user
    assert project_user.role == projects_users_models.ProjectUserRole.MANAGER
    assert (
        project_user.permission
        == projects_users_models.ProjectUserPermission.WRITE
    )


def test_http_exception_when_updating_permission_of_manager(
    db: orm.Session,
    client: testclient.TestClient,
    executor_name: str,
    unique_username: str,
    project: projects_models.DatabaseProject,
):
    users_crud.create_user(db, executor_name, users_models.Role.ADMIN)
    user = users_crud.create_user(db, unique_username, users_models.Role.USER)

    projects_users_crud.add_user_to_project(
        db,
        project,
        user,
        projects_users_models.ProjectUserRole.MANAGER,
        projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user.id}",
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
            visibility=projects_models.Visibility.INTERNAL
        ),
    )
    users_crud.create_user(db, executor_name, users_models.Role.USER)

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
            visibility=projects_models.Visibility.PRIVATE
        ),
    )
    users_crud.create_user(db, executor_name, users_models.Role.USER)

    response = client.get(
        f"/api/v1/projects/{project.slug}/users/current",
    )

    assert response.status_code == 404
    assert "detail" in response.json()
    assert "reason" in response.json()["detail"]
