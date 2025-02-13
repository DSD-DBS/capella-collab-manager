# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import uuid

import pytest
import sqlalchemy as sa
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.configuration.app import config
from capellacollab.events import models as events_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.users import crud as projects_users_crud
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import crud as users_crud
from capellacollab.users import models as users_models

reason: str = "TestReason"


@pytest.fixture(name="unique_username")
def fixture_unique_username() -> str:
    return str(uuid.uuid1())


def test_create_admin_user_by_system(db: orm.Session):
    user = users_crud.get_user_by_name(db, config.initial.admin)
    assert user is not None

    events: list[events_models.DatabaseUserHistoryEvent] = (
        get_events_by_user_id(db, user.id)
    )

    assert len(events) == 1

    event: events_models.DatabaseUserHistoryEvent = events[0]

    assert event.event_type == events_models.EventType.CREATED_USER
    assert event.executor is None
    assert event.reason is None
    assert event.project is None
    assert event.user_id == user.id


def test_create_user_created_event(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    unique_username: str,
):
    response = client.post(
        "/api/v1/users",
        json={
            "name": unique_username,
            "role": "user",
            "reason": reason,
            "idp_identifier": "test",
        },
    )

    events = get_events_by_username(db, unique_username)

    assert response.status_code == 200
    assert len(events) == 1

    event = events[0]

    assert event.event_type == events_models.EventType.CREATED_USER
    assert event.executor_id == admin.id
    assert event.reason == "TestReason"
    assert event.project is None
    assert event.user_id == int(response.json()["id"])


def test_user_deleted_cleanup(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    unique_username: str,
):
    response = client.post(
        "/api/v1/users",
        json={
            "name": unique_username,
            "idp_identifier": "test",
            "role": "user",
            "reason": reason,
        },
    )

    assert response.status_code == 200
    assert len(get_events_by_username(db, unique_username)) == 1
    assert len(get_executed_events_by_user_id(db, admin.id)) == 1

    user_id = int(response.json()["id"])
    response = client.delete(f"/api/v1/users/{user_id}")

    assert response.status_code == 204
    assert not get_events_by_username(db, unique_username)
    assert not get_executed_events_by_user_id(db, admin.id)


@pytest.mark.parametrize(
    ("initial_role", "target_role", "expected_event_type"),
    [
        (
            users_models.Role.USER,
            users_models.Role.ADMIN,
            events_models.EventType.ASSIGNED_ROLE_ADMIN,
        ),
        (
            users_models.Role.ADMIN,
            users_models.Role.USER,
            events_models.EventType.ASSIGNED_ROLE_USER,
        ),
    ],
)
def test_create_assign_user_role_event(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    unique_username: str,
    initial_role: users_models.Role,
    target_role: users_models.Role,
    expected_event_type: events_models.EventType,
):
    user = users_crud.create_user(
        db, unique_username, unique_username, None, initial_role
    )

    response = client.patch(
        f"/api/v1/users/{user.id}",
        json={"role": target_role.value, "reason": reason},
    )

    events = get_events_by_username(db, unique_username)

    assert response.status_code == 200
    assert len(events) == 1

    event = events[0]

    assert event.event_type == expected_event_type
    assert event.executor_id == admin.id
    assert event.reason == reason
    assert event.project is None
    assert event.user_id == user.id


@pytest.mark.parametrize(
    ("permission", "expected_permission_event_type"),
    [
        (
            projects_users_models.ProjectUserPermission.READ,
            events_models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY,
        ),
        (
            projects_users_models.ProjectUserPermission.WRITE,
            events_models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE,
        ),
    ],
)
@pytest.mark.usefixtures("admin")
def test_create_user_added_to_project_event(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    permission: projects_users_models.ProjectUserPermission,
    expected_permission_event_type: events_models.EventType,
    user2: users_models.DatabaseUser,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/users/",
        json={
            "role": projects_users_models.ProjectUserRole.USER.value,
            "permission": permission.value,
            "username": user2.name,
            "reason": reason,
        },
    )

    assert response.status_code == 200

    events = get_events_by_user_id(db, user2.id)
    assert len(events) == 3

    user_added_event = events[0]
    assert (
        user_added_event.event_type == events_models.EventType.ADDED_TO_PROJECT
    )
    assert user_added_event.executor_id == admin.id
    assert user_added_event.reason == reason
    assert user_added_event.project_id == project.id
    assert user_added_event.user_id == user2.id

    assert (
        events[1].event_type
        == events_models.EventType.ASSIGNED_PROJECT_ROLE_USER
    )
    assert events[2].event_type == expected_permission_event_type


def test_create_user_removed_from_project_event(
    client: testclient.TestClient,
    db: orm.Session,
    user2: users_models.DatabaseUser,
    admin: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
):
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        projects_users_models.ProjectUserRole.USER,
        projects_users_models.ProjectUserPermission.READ,
    )

    response = client.request(
        "DELETE",
        f"/api/v1/projects/{project.slug}/users/{user2.id}",
        content=reason,
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 204

    events = get_events_by_user_id(db, user2.id)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == events_models.EventType.REMOVED_FROM_PROJECT
    assert event.executor_id == admin.id
    assert event.reason == reason
    assert event.project_id == project.id
    assert event.user_id == user2.id


def test_create_manager_added_to_project_event(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    user2: users_models.DatabaseUser,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/users/",
        json={
            "role": projects_users_models.ProjectUserRole.MANAGER.value,
            "permission": projects_users_models.ProjectUserPermission.READ.value,
            "username": user2.name,
            "reason": reason,
        },
    )

    events = get_events_by_user_id(db, user2.id)

    assert response.status_code == 200
    assert len(events) == 2

    for event, expected_event_type in zip(
        events,
        [
            events_models.EventType.ADDED_TO_PROJECT,
            events_models.EventType.ASSIGNED_PROJECT_ROLE_MANAGER,
        ],
    ):
        assert event.event_type == expected_event_type
        assert event.executor_id == admin.id
        assert event.reason == reason
        assert event.project_id == project.id
        assert event.user_id == user2.id


@pytest.mark.parametrize(
    ("initial_permission", "target_permission", "expected_permission_event_type"),
    [
        (
            projects_users_models.ProjectUserPermission.READ,
            projects_users_models.ProjectUserPermission.WRITE,
            events_models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE,
        ),
        (
            projects_users_models.ProjectUserPermission.WRITE,
            projects_users_models.ProjectUserPermission.READ,
            events_models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY,
        ),
    ],
)
def test_create_user_permission_change_event(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    initial_permission: projects_users_models.ProjectUserPermission,
    target_permission: projects_users_models.ProjectUserPermission,
    expected_permission_event_type: events_models.EventType,
    user2: users_models.DatabaseUser,
):
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        projects_users_models.ProjectUserRole.USER,
        initial_permission,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user2.id}",
        json={
            "permission": target_permission.value,
            "reason": reason,
        },
    )

    assert response.status_code == 204

    events = get_events_by_user_id(db, user2.id)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == expected_permission_event_type
    assert event.executor_id == admin.id
    assert event.reason == reason
    assert event.project_id == project.id
    assert event.user_id == user2.id


@pytest.mark.parametrize(
    ("initial_role", "target_role", "expected_role_event_type"),
    [
        (
            projects_users_models.ProjectUserRole.USER,
            projects_users_models.ProjectUserRole.MANAGER,
            events_models.EventType.ASSIGNED_PROJECT_ROLE_MANAGER,
        ),
        (
            projects_users_models.ProjectUserRole.MANAGER,
            projects_users_models.ProjectUserRole.USER,
            events_models.EventType.ASSIGNED_PROJECT_ROLE_USER,
        ),
    ],
)
def test_create_user_role_change_event(
    client: testclient.TestClient,
    db: orm.Session,
    admin: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    initial_role: projects_users_models.ProjectUserRole,
    target_role: projects_users_models.ProjectUserRole,
    expected_role_event_type: events_models.EventType,
    user2: users_models.DatabaseUser,
):
    projects_users_crud.add_user_to_project(
        db,
        project,
        user2,
        initial_role,
        projects_users_models.ProjectUserPermission.READ,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user2.id}",
        json={
            "role": target_role.value,
            "reason": reason,
        },
    )

    assert response.status_code == 204

    events = get_events_by_user_id(db, user2.id)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == expected_role_event_type
    assert event.executor_id == admin.id
    assert event.reason == reason
    assert event.project_id == project.id
    assert event.user_id == user2.id


def get_events_by_username(
    db: orm.Session, username: str
) -> list[events_models.DatabaseUserHistoryEvent]:
    if not (user := users_crud.get_user_by_name(db, username)):
        return []
    return user.events


def get_events_by_user_id(
    db: orm.Session, user_id: int
) -> list[events_models.DatabaseUserHistoryEvent]:
    if not (user := users_crud.get_user_by_id(db, user_id)):
        return []
    return user.events


def get_executed_events_by_user_id(db: orm.Session, user_id: int):
    return (
        db.execute(
            sa.select(events_models.DatabaseUserHistoryEvent).where(
                events_models.DatabaseUserHistoryEvent.executor_id == user_id
            )
        )
        .scalars()
        .all()
    )
