# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import enum
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.projects.models import Project
from capellacollab.users.models import User


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
    execution_time: datetime
    event_type: EventType
    reason: str | None

    class Config:
        orm_mode = True


class HistoryEvent(BaseHistoryEvent):
    id: str


class UserHistory(User):
    created: datetime | None
    last_login: datetime | None
    events: list[HistoryEvent] | None


class DatabaseUserHistoryEvent(Base):
    __tablename__ = "user_history_events"
    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship(
        "DatabaseUser", back_populates="events", foreign_keys=[user_id]
    )

    executor_id = Column(Integer, ForeignKey("users.id"))
    executor = relationship("DatabaseUser", foreign_keys=[executor_id])

    project_id = Column(Integer, ForeignKey("projects.id"))
    project = relationship("DatabaseProject", foreign_keys=[project_id])

    execution_time = Column(DateTime)
    event_type = Column(Enum(EventType))
    reason = Column(String)
