# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel, validator
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

# Import required for sqlalchemy
import capellacollab.projects.capellamodels.models
from capellacollab.core.database import Base
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    ProjectUserPermission,
    ProjectUserRole,
)


class UserMetadata(BaseModel):
    leads: int
    contributors: int
    subscribers: int


class Project(BaseModel):
    name: str
    slug: str
    description: t.Optional[str]
    users: UserMetadata

    @validator("users", pre=True)
    def transform_users(
        cls, users: t.Union[UserMetadata, t.List[ProjectUserAssociation]]
    ):
        if isinstance(users, UserMetadata):
            return users

        return UserMetadata(
            leads=len(
                [
                    user
                    for user in users
                    if user.role == ProjectUserRole.MANAGER
                ]
            ),
            contributors=len(
                [
                    user
                    for user in users
                    if user.role == ProjectUserRole.USER
                    and user.permission == ProjectUserPermission.WRITE
                ]
            ),
            subscribers=len(
                [
                    user
                    for user in users
                    if user.role == ProjectUserRole.USER
                    and user.permission == ProjectUserPermission.READ
                ]
            ),
        )

    class Config:
        orm_mode = True


class PatchProject(BaseModel):
    description: str


class PostProjectRequest(BaseModel):
    name: str
    description: t.Optional[str]


class DatabaseProject(Base):
    __tablename__ = "projects"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    users: ProjectUserAssociation = relationship(
        "ProjectUserAssociation",
        back_populates="projects",
    )
    models: DatabaseCapellaModel = relationship(
        "DatabaseCapellaModel", back_populates="project"
    )
