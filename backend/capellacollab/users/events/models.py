# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.projects.models import Project
from capellacollab.users.models import User


class EventType(enum.Enum):
    CREATED = "Created"
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
    executor: t.Optional[User]
    project: t.Optional[Project]
    execution_time: datetime
    event_type: EventType
    reason: t.Optional[str]

    class Config:
        orm_mode = True


class HistoryEvent(BaseHistoryEvent):
    id: str


class UserHistory(User):
    created: datetime
    last_login: t.Optional[datetime]
    events: t.Optional[list[HistoryEvent]]


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
