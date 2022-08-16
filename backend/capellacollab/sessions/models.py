# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

# 3rd party:
from sqlalchemy import ARRAY, TIMESTAMP, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

# 1st party:
from capellacollab.core.database import Base
from capellacollab.sessions.schema import WorkspaceType


class DatabaseSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    owner_name = Column(String, ForeignKey("users.name"))
    owner = relationship("DatabaseUser")
    ports = Column(ARRAY(Integer))
    created_at = Column(TIMESTAMP)
    rdp_password = Column(String)
    guacamole_username = Column(String)
    guacamole_password = Column(String)
    guacamole_connection_id = Column(String)
    host = Column(String)
    type = Column(Enum(WorkspaceType), nullable=False)
    repository = Column(String)
    mac = Column(String)
