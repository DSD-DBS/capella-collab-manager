# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


from __future__ import annotations

import typing as t

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

if t.TYPE_CHECKING:
    from datetime import datetime

    from capellacollab.users.models import DatabaseUser


class DatabaseSession(Base):
    __tablename__ = "sessions"

    id: str = Column(String, primary_key=True, index=True)
    owner_name: str = Column(String, ForeignKey("users.name"))
    owner: DatabaseUser = relationship("DatabaseUser")
    ports: list[int] = Column(ARRAY(Integer))
    created_at: datetime = Column(TIMESTAMP)
    t4c_password: str = Column(String, nullable=True)
    rdp_password: str = Column(String)
    guacamole_username: str = Column(String)
    guacamole_password: str = Column(String)
    guacamole_connection_id: str = Column(String)
    host: str = Column(String)
    type: WorkspaceType = Column(Enum(WorkspaceType), nullable=False)
    repository: str = Column(String)
    mac: str = Column(String)
