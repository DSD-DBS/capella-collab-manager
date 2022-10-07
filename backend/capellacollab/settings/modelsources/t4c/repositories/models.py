# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base


class DatabaseT4CRepository(Base):
    __tablename__ = "t4c_repositories"
    __table_args__ = (UniqueConstraint("instance_id", "name"),)

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    instance_id = Column(
        Integer, ForeignKey("t4c_instances.id"), nullable=False
    )

    instance = relationship(
        "DatabaseT4CInstance", back_populates="repositories"
    )
