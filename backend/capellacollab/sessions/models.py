# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import typing as t
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base
from capellacollab.sessions.schema import WorkspaceType
from capellacollab.tools.models import Tool, Version

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.users.models import DatabaseUser


class DatabaseSession(Base):
    __tablename__ = "sessions"

    id: str = Column(String, primary_key=True, index=True)
    owner_name: str = Column(String, ForeignKey("users.name"))
    owner: DatabaseUser = relationship("DatabaseUser")
    tool_id: int = Column(Integer, ForeignKey(Tool.id))
    tool: Tool = relationship(Tool)

    version_id: int = Column(Integer, ForeignKey(Version.id))
    version: Version = relationship(Version)
    ports: list[int] = Column(ARRAY(Integer))
    created_at: datetime = Column(TIMESTAMP)
    t4c_password: str = Column(String, nullable=True)
    rdp_password: str = Column(String)
    guacamole_username: str = Column(String)
    guacamole_password: str = Column(String)
    guacamole_connection_id: str = Column(String)
    host: str = Column(String)
    type: WorkspaceType = Column(Enum(WorkspaceType), nullable=False)
    project_id: str = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project: "DatabaseProject" = relationship("DatabaseProject")
    mac: str = Column(String)
