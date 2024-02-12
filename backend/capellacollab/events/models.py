# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum
import typing as t

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects import models as projects_models
from capellacollab.users import models as users_models

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.users.models import DatabaseUser


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


class BaseHistoryEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: users_models.User = Field(
        description="The user affected by an event",
        examples=[{"id": 2, "name": "John Doe", "role": "user"}],
    )
    executor: users_models.User | None = Field(
        default=None,
        description="The user who executed an event",
        examples=[{"id": 1, "name": "Joe Manager", "role": "admin"}],
    )
    project: projects_models.Project | None = Field(
        default=None,
        description="The project affected by an event",
        examples=[{"id": 1, "name": "Project A"}],
    )
    execution_time: datetime.datetime = Field(
        default=None,
        description="The time an event was executed",
        examples=["2021-01-01T12:00:00Z"],
    )
    event_type: EventType = Field(
        description="The type of event executed", examples=["CreatedUser"]
    )
    reason: str | None = Field(
        description="The rationale provided by the executor of an event",
        examples=["New hire"],
        max_length=255,
    )

    _validate_execution_time = field_serializer("execution_time")(
        core_pydantic.datetime_serializer
    )


class HistoryEvent(BaseHistoryEvent):
    id: int


class DatabaseUserHistoryEvent(database.Base):
    __tablename__ = "user_history_events"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True, index=True)

    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("users.id"))
    user: orm.Mapped["DatabaseUser"] = orm.relationship(
        back_populates="events", foreign_keys=[user_id]
    )

    executor_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("users.id")
    )
    executor: orm.Mapped["DatabaseUser"] = orm.relationship(
        foreign_keys=[executor_id]
    )

    project_id: orm.Mapped[int | None] = orm.mapped_column(
        sa.ForeignKey("projects.id")
    )
    project: orm.Mapped["DatabaseProject"] = orm.relationship(
        foreign_keys=[project_id]
    )

    execution_time: orm.Mapped[datetime.datetime]
    event_type: orm.Mapped[EventType]
    reason: orm.Mapped[str | None]
