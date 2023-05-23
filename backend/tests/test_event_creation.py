# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.config import config
from capellacollab.projects.users.crud import add_user_to_project
from capellacollab.projects.users.models import (
    ProjectUserPermission,
    ProjectUserRole,
)
from capellacollab.users.crud import (
    create_user,
    get_user_by_id,
    get_user_by_name,
)
from capellacollab.users.events.models import (
    DatabaseUserHistoryEvent,
    EventType,
)
from capellacollab.users.models import DatabaseUser, Role

reason: str = "TestReason"


def test_create_admin_user_by_system(db):
    user: DatabaseUser = get_user_by_name(db, config["initial"]["admin"])

    events: list[DatabaseUserHistoryEvent] = get_events_by_user_id(db, user.id)

    assert len(events) == 1

    event: DatabaseUserHistoryEvent = events[0]

    assert event.event_type == EventType.CREATED_USER
    assert event.executor is None
    assert event.reason is None
    assert event.project is None
    assert event.user_id == user.id


def test_create_user_created_event(client, db, executor_name, unique_username):
    executor = create_user(db, executor_name, Role.ADMIN)

    response = client.post(
        "/api/v1/users/",
        json={"name": unique_username, "role": "user", "reason": reason},
    )

    events = get_events_by_username(db, unique_username)

    assert response.status_code == 200
    assert len(events) == 1

    event = events[0]

    assert event.event_type == EventType.CREATED_USER
    assert event.executor_id == executor.id
    assert event.reason == "TestReason"
    assert event.project is None
    assert event.user_id == int(response.json()["id"])


def test_user_deleted_cleanup(client, db, executor_name, unique_username):
    executor = create_user(db, executor_name, Role.ADMIN)

    response = client.post(
        "/api/v1/users/",
        json={"name": unique_username, "role": "user", "reason": reason},
    )

    assert response.status_code == 200
    assert len(get_events_by_username(db, unique_username)) == 1
    assert len(get_executed_events_by_user_id(db, executor.id)) == 1

    user_id = int(response.json()["id"])
    response = client.delete(f"/api/v1/users/{user_id}")

    assert response.status_code == 204
    assert not get_events_by_username(db, unique_username)
    assert not get_executed_events_by_user_id(db, executor.id)


@pytest.mark.parametrize(
    "initial_role,target_role,expected_event_type",
    [
        (Role.USER, Role.ADMIN, EventType.ASSIGNED_ROLE_ADMIN),
        (Role.ADMIN, Role.USER, EventType.ASSIGNED_ROLE_USER),
    ],
)
def test_create_assign_user_role_event(
    client,
    db,
    executor_name,
    unique_username,
    initial_role,
    target_role,
    expected_event_type,
):
    executor = create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, initial_role)

    response = client.patch(
        f"/api/v1/users/{user.id}/roles",
        json={"role": target_role.value, "reason": reason},
    )

    events = get_events_by_username(db, unique_username)

    assert response.status_code == 200
    assert len(events) == 1

    event = events[0]

    assert event.event_type == expected_event_type
    assert event.executor_id == executor.id
    assert event.reason == reason
    assert event.project is None
    assert event.user_id == user.id


@pytest.mark.parametrize(
    "permission,expected_permission_event_type",
    [
        (
            ProjectUserPermission.READ,
            EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY,
        ),
        (
            ProjectUserPermission.WRITE,
            EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE,
        ),
    ],
)
def test_create_user_added_to_project_event(
    client,
    db,
    executor_name,
    unique_username,
    project,
    permission,
    expected_permission_event_type,
):
    executor = create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    response = client.post(
        f"/api/v1/projects/{project.slug}/users/",
        json={
            "role": ProjectUserRole.USER.value,
            "permission": permission.value,
            "username": user.name,
            "reason": reason,
        },
    )

    assert response.status_code == 200

    events = get_events_by_user_id(db, user.id)
    assert len(events) == 3

    user_added_event = events[0]
    assert user_added_event.event_type == EventType.ADDED_TO_PROJECT
    assert user_added_event.executor_id == executor.id
    assert user_added_event.reason == reason
    assert user_added_event.project_id == project.id
    assert user_added_event.user_id == user.id

    assert events[1].event_type == EventType.ASSIGNED_PROJECT_ROLE_USER
    assert events[2].event_type == expected_permission_event_type


def test_create_user_removed_from_project_event(
    client, db, executor_name, unique_username, project
):
    executor = create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    add_user_to_project(
        db, project, user, ProjectUserRole.USER, ProjectUserPermission.READ
    )

    response = client.request(
        "DELETE",
        f"/api/v1/projects/{project.slug}/users/{user.id}",
        data=reason,
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 204

    events = get_events_by_user_id(db, user.id)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == EventType.REMOVED_FROM_PROJECT
    assert event.executor_id == executor.id
    assert event.reason == reason
    assert event.project_id == project.id
    assert event.user_id == user.id


def test_create_manager_added_to_project_event(
    client, db, executor_name, unique_username, project
):
    executor = create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    response = client.post(
        f"/api/v1/projects/{project.slug}/users/",
        json={
            "role": ProjectUserRole.MANAGER.value,
            "permission": ProjectUserPermission.READ.value,
            "username": user.name,
            "reason": reason,
        },
    )

    events = get_events_by_user_id(db, user.id)

    assert response.status_code == 200
    assert len(events) == 2

    for event, expected_event_type in zip(
        events,
        [
            EventType.ADDED_TO_PROJECT,
            EventType.ASSIGNED_PROJECT_ROLE_MANAGER,
        ],
    ):
        assert event.event_type == expected_event_type
        assert event.executor_id == executor.id
        assert event.reason == reason
        assert event.project_id == project.id
        assert event.user_id == user.id


@pytest.mark.parametrize(
    "initial_permission,target_permission,expected_permission_event_type",
    [
        (
            ProjectUserPermission.READ,
            ProjectUserPermission.WRITE,
            EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE,
        ),
        (
            ProjectUserPermission.WRITE,
            ProjectUserPermission.READ,
            EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY,
        ),
    ],
)
def test_create_user_permission_change_event(
    client,
    db,
    executor_name,
    unique_username,
    project,
    initial_permission,
    target_permission,
    expected_permission_event_type,
):
    executor = create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    add_user_to_project(
        db, project, user, ProjectUserRole.USER, initial_permission
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user.id}",
        json={
            "permission": target_permission.value,
            "reason": reason,
        },
    )

    assert response.status_code == 204

    events = get_events_by_user_id(db, user.id)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == expected_permission_event_type
    assert event.executor_id == executor.id
    assert event.reason == reason
    assert event.project_id == project.id
    assert event.user_id == user.id


@pytest.mark.parametrize(
    "initial_role,target_role,expected_role_event_type",
    [
        (
            ProjectUserRole.USER,
            ProjectUserRole.MANAGER,
            EventType.ASSIGNED_PROJECT_ROLE_MANAGER,
        ),
        (
            ProjectUserRole.MANAGER,
            ProjectUserRole.USER,
            EventType.ASSIGNED_PROJECT_ROLE_USER,
        ),
    ],
)
def test_create_user_role_change_event(
    client,
    db,
    executor_name,
    unique_username,
    project,
    initial_role,
    target_role,
    expected_role_event_type,
):
    executor = create_user(db, executor_name, Role.ADMIN)
    user = create_user(db, unique_username, Role.USER)

    add_user_to_project(
        db, project, user, initial_role, ProjectUserPermission.READ
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/users/{user.id}",
        json={
            "role": target_role.value,
            "reason": reason,
        },
    )

    assert response.status_code == 204

    events = get_events_by_user_id(db, user.id)
    assert len(events) == 1

    event = events[0]

    assert event.event_type == expected_role_event_type
    assert event.executor_id == executor.id
    assert event.reason == reason
    assert event.project_id == project.id
    assert event.user_id == user.id


def get_events_by_username(
    db: Session, username: str
) -> list[DatabaseUserHistoryEvent]:
    if not (user := get_user_by_name(db, username)):
        return []
    return user.events


def get_events_by_user_id(
    db: Session, user_id: int
) -> list[DatabaseUserHistoryEvent]:
    if not (user := get_user_by_id(db, user_id)):
        return []
    return user.events


def get_executed_events_by_user_id(db: Session, user_id: int):
    return (
        db.execute(
            select(DatabaseUserHistoryEvent).where(
                DatabaseUserHistoryEvent.executor_id == user_id
            )
        )
        .scalars()
        .all()
    )
