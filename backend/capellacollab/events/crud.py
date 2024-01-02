# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.users import models as users_models

from . import models


def create_event(
    db: orm.Session,
    user: users_models.DatabaseUser,
    event_type: models.EventType,
    executor: users_models.DatabaseUser | None = None,
    project: projects_models.DatabaseProject | None = None,
    reason: str | None = None,
    allowed_types: list[models.EventType] | None = None,
) -> models.DatabaseUserHistoryEvent:
    if allowed_types and event_type not in allowed_types:
        raise ValueError(
            f"Event type must of one of the following: {allowed_types}"
        )
    event = models.DatabaseUserHistoryEvent(
        user_id=user.id,
        event_type=event_type,
        execution_time=datetime.datetime.now(datetime.UTC),
        executor_id=executor.id if executor else None,
        project_id=project.id if project else None,
        reason=reason,
    )
    db.add(event)
    db.commit()

    return event


def create_user_creation_event(
    db: orm.Session,
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
    db: orm.Session,
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
    db: orm.Session,
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


def get_events(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseUserHistoryEvent]:
    return (
        db.execute(sa.select(models.DatabaseUserHistoryEvent)).scalars().all()
    )


def delete_all_events_user_involved_in(db: orm.Session, user_id: int):
    db.execute(
        sa.delete(models.DatabaseUserHistoryEvent).where(
            (models.DatabaseUserHistoryEvent.user_id == user_id)
            | (models.DatabaseUserHistoryEvent.executor_id == user_id)
        )
    )
    db.commit()


def delete_all_events_projects_associated_with(
    db: orm.Session, project_id: int
):
    db.execute(
        sa.delete(models.DatabaseUserHistoryEvent).where(
            models.DatabaseUserHistoryEvent.project_id == project_id
        )
    )
    db.commit()
