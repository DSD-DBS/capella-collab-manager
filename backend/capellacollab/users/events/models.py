# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import datetime
import enum

from pydantic import BaseModel
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from capellacollab.core.database import Base
from capellacollab.projects.models import DatabaseProject, Project
from capellacollab.users.models import DatabaseUser, User


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
    user: User
    executor: User | None
    project: Project | None
    execution_time: datetime.datetime
    event_type: EventType
    reason: str | None

    class Config:
        orm_mode = True


class HistoryEvent(BaseHistoryEvent):
    id: str


class UserHistory(User):
    created: datetime.datetime | None
    last_login: datetime.datetime | None
    events: list[HistoryEvent] | None


class DatabaseUserHistoryEvent(Base):
    __tablename__ = "user_history_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["DatabaseUser"] = relationship(
        back_populates="events", foreign_keys=[user_id]
    )

    executor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    executor: Mapped["DatabaseUser"] = relationship(foreign_keys=[executor_id])

    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["DatabaseProject"] = relationship(
        foreign_keys=[project_id]
    )

    execution_time: Mapped[datetime.datetime]
    event_type: Mapped[EventType]
    reason: Mapped[str | None]
