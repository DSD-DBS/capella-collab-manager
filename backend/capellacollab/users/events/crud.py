# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t
from datetime import datetime

from sqlalchemy.orm import Session

from capellacollab.projects import models as projects_models
from capellacollab.users import models as users_models
from capellacollab.users.events import models


def create_event(
    db: Session,
    user: users_models.DatabaseUser,
    event_type: models.EventType,
    executor: users_models.DatabaseUser | None = None,
    project: projects_models.DatabaseProject | None = None,
    reason: str | None = None,
    allowed_types: t.Optional[list[models.EventType]] = None,
) -> models.DatabaseUserHistoryEvent:
    if allowed_types and event_type not in allowed_types:
        raise ValueError(
            f"Event type must of one of the following: {allowed_types}"
        )
    event = models.DatabaseUserHistoryEvent(
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
    user: users_models.DatabaseUser,
    executor: users_models.DatabaseUser | None = None,
    reason: str | None = None,
):
    return create_event(
        db=db,
        user=user,
        event_type=models.EventType.CREATED_USER,
        executor=executor,
        reason=reason,
    )


def create_role_change_event(
    db: Session,
    user: users_models.DatabaseUser,
    event_type: models.EventType,
    executor: users_models.DatabaseUser,
    reason: str,
) -> models.DatabaseUserHistoryEvent:
    return create_event(
        db=db,
        user=user,
        event_type=event_type,
        executor=executor,
        reason=reason,
        allowed_types=[
            models.EventType.ASSIGNED_ROLE_ADMIN,
            models.EventType.ASSIGNED_ROLE_USER,
        ],
    )


def create_project_change_event(
    db: Session,
    user: users_models.DatabaseUser,
    event_type: models.EventType,
    executor: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
    reason: str,
) -> models.DatabaseUserHistoryEvent:
    return create_event(
        db=db,
        user=user,
        event_type=event_type,
        executor=executor,
        project=project,
        reason=reason,
        allowed_types=[
            models.EventType.ADDED_TO_PROJECT,
            models.EventType.REMOVED_FROM_PROJECT,
            models.EventType.ASSIGNED_PROJECT_ROLE_MANAGER,
            models.EventType.ASSIGNED_PROJECT_ROLE_USER,
            models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_ONLY,
            models.EventType.ASSIGNED_PROJECT_PERMISSION_READ_WRITE,
        ],
    )


def get_events(db: Session) -> list[models.DatabaseUserHistoryEvent]:
    return db.query(models.DatabaseUserHistoryEvent).all()


def delete_all_events_involved_in(
    db: Session, user: users_models.DatabaseUser
):
    db.query(models.DatabaseUserHistoryEvent).filter(
        (models.DatabaseUserHistoryEvent.user_id == user.id)
        | (models.DatabaseUserHistoryEvent.executor_id == user.id)
    ).delete()
    db.commit()
