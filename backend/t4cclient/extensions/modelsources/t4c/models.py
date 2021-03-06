# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from t4cclient.core.database import Base


class DatabaseProject(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    repository_name = Column(
        String, ForeignKey("repositories.name", ondelete="CASCADE")
    )
    repository = relationship("DatabaseRepository", back_populates="projects")
