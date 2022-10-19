# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum

from pydantic import BaseModel
from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from capellacollab.core.database import Base


class Role(enum.Enum):
    USER = "user"
    ADMIN = "administrator"


class BaseUser(BaseModel):
    name: str
    role: Role

    class Config:
        orm_mode = True


class User(BaseUser):
    id: str


class PatchUserRoleRequest(BaseModel):
    role: Role


class DatabaseUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    role = Column(Enum(Role))
    projects = relationship(
        "ProjectUserAssociation",
        back_populates="user",
    )
    sessions = relationship(
        "DatabaseSession",
        back_populates="owner",
    )
