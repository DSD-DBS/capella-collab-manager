# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import enum
import typing as t

import pydantic
import sqlalchemy as sa
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


class BaseHistoryEvent(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    user: users_models.User
    executor: users_models.User | None = None
    project: projects_models.Project | None = None
    execution_time: datetime.datetime
    event_type: EventType
    reason: str | None = None

    _validate_execution_time = pydantic.field_validator("execution_time")(
        core_pydantic.datetime_serializer
    )


class HistoryEvent(BaseHistoryEvent):
    id: int


class UserHistory(users_models.User):
    created: datetime.datetime | None = None
    last_login: datetime.datetime | None = None
    events: list[HistoryEvent] | None = None

    _validate_created = pydantic.field_validator("created")(
        core_pydantic.datetime_serializer
    )
    _validate_last_login = pydantic.field_validator("last_login")(
        core_pydantic.datetime_serializer
    )


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
