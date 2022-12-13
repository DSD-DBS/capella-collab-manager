# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from datetime import datetime

from sqlalchemy.orm import Session

from capellacollab.projects.models import DatabaseProject
from capellacollab.users.crud import get_user_by_name
from capellacollab.users.events.models import (
    DatabaseUserHistoryEvent,
    EventType,
)
from capellacollab.users.models import DatabaseUser


def create_event(
    db: Session,
    user: DatabaseUser,
    event_type: EventType,
    executor: DatabaseUser | None = None,
    project: DatabaseProject | None = None,
    reason: str | None = None,
    allowed_types: t.Optional[list[EventType]] = None,
) -> DatabaseUserHistoryEvent:
    if allowed_types and event_type not in allowed_types:
        raise ValueError(
            f"Event type must of one of the following: {allowed_types}"
        )
    event = DatabaseUserHistoryEvent(
        user_id=user.id,
        event_type=event_type,
        execution_time=datetime.now(),
        executor_id=executor.id if executor else None,
        project_id=project.id if project else None,
        reason=reason,
    )
    db.add(event)
    db.commit()

    return event


def create_user_creation_event(
    db: Session,
    user: DatabaseUser,
    executor: t.Optional[DatabaseUser] = None,
    reason: t.Optional[str] = None,
) -> DatabaseUserHistoryEvent:
    return create_event(
        db=db,
        user=user,
        event_type=EventType.CREATED,
        executor=executor,
        reason=reason,
    )


def create_role_change_event(
    db: Session,
    user: DatabaseUser,
    event_type: EventType,
    executor: DatabaseUser,
    reason: str,
) -> DatabaseUserHistoryEvent:
    return create_event(
        db=db,
        user=user,
        event_type=event_type,
        executor=executor,
        reason=reason,
        allowed_types=[
            EventType.ASSIGNED_ROLE_ADMIN,
            EventType.ASSIGNED_ROLE_USER,
        ],
    )


def create_project_change_event(
    db: Session,
    user: DatabaseUser,
    event_type: EventType,
    executor: DatabaseUser,
    project: DatabaseProject,
    reason: str,
) -> DatabaseUserHistoryEvent:
    return create_event(
        db=db,
        user=user,
        event_type=event_type,
        executor=executor,
        project=project,
        reason=reason,
        allowed_types=[
            EventType.ADDED_TO_PROJECT,
            EventType.REMOVED_FROM_PROJECT,
            EventType.ASSIGNED_PROJECT_ROLE_MANAGER,
            EventType.ASSIGNED_PROJECT_ROLE_USER,
            EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY,
            EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE,
        ],
    )


def get_events(db: Session) -> list[DatabaseUserHistoryEvent]:
    return db.query(DatabaseUserHistoryEvent).all()


def get_events_by_username(
    db: Session, username: str
) -> list[DatabaseUserHistoryEvent]:
    user: DatabaseUser = get_user_by_name(db, username)
    return get_events_by_user_id(db, user.id)


def get_events_by_user_id(
    db: Session, user_id: int
) -> list[DatabaseUserHistoryEvent]:
    return (
        db.query(DatabaseUserHistoryEvent)
        .filter(DatabaseUserHistoryEvent.user_id == user_id)
        .all()
    )
