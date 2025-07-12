# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects import models as projects_models
from capellacollab.users import models as users_models


class EventType(enum.Enum):
    CREATED_USER = "CreatedUser"
    ADDED_TO_PROJECT = "AddedToProject"
    REMOVED_FROM_PROJECT = "RemovedFromProject"
    ASSIGNED_PROJECT_ROLE_USER = "AssignedProjectRoleUser"
    ASSIGNED_PROJECT_ROLE_MANAGER = "AssignedProjectRoleManager"
    ASSIGNED_PROJECT_PERMISSION_READ_ONLY = "AssignedProjectPermissionReadOnly"
    ASSIGNED_PROJECT_PERMISSION_READ_WRITE = (
        "AssignedProjectPermissionReadWrite"
    )
    ASSIGNED_ROLE_ADMIN = "AssignedRoleAdmin"
    ASSIGNED_ROLE_USER = "AssignedRoleUser"
    BLOCKED_USER = "UserBlocked"
    UNBLOCKED_USER = "UserUnblocked"


class BaseHistoryEvent(core_pydantic.BaseModel):
    user: users_models.User
    executor: users_models.User | None = None
    project: projects_models.Project | None = None
    execution_time: datetime.datetime
    event_type: EventType
    reason: str | None = None

    _validate_execution_time = pydantic.field_serializer("execution_time")(
        core_pydantic.datetime_serializer
    )


class HistoryEvent(BaseHistoryEvent):
    id: int


class DatabaseUserHistoryEvent(database.Base):
    __tablename__ = "user_history_events"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"),
        init=False,
    )
    user: orm.Mapped[users_models.DatabaseUser] = orm.relationship(
        back_populates="events", foreign_keys=[user_id]
    )

    event_type: orm.Mapped[EventType]
    reason: orm.Mapped[str | None] = orm.mapped_column(default=None)

    executor_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("users.id"),
        init=False,
    )
    executor: orm.Mapped[users_models.DatabaseUser | None] = orm.relationship(
        default=None, foreign_keys=[executor_id]
    )

    project_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("projects.id"),
        init=False,
    )
    project: orm.Mapped[projects_models.DatabaseProject | None] = (
        orm.relationship(default=None, foreign_keys=[project_id])
    )

    execution_time: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )
