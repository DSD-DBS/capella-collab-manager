# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

from pydantic import BaseModel, validator
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import required for sqlalchemy
from capellacollab.core.database import Base
from capellacollab.projects.users.models import (
    ProjectUserAssociation,
    ProjectUserPermission,
    ProjectUserRole,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel


class UserMetadata(BaseModel):
    leads: int
    contributors: int
    subscribers: int


class Project(BaseModel):
    name: str
    slug: str
    description: str | None
    users: UserMetadata

    @validator("users", pre=True)
    @classmethod
    def transform_users(
        cls, users: UserMetadata | list[ProjectUserAssociation]
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
    name: str | None
    description: str | None


class PostProjectRequest(BaseModel):
    name: str
    description: str | None


class DatabaseProject(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(unique=True, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(unique=True, index=True)
    slug: Mapped[str] = mapped_column(unique=True, index=True)
    description: Mapped[str | None]

    users: Mapped[list[ProjectUserAssociation]] = relationship(
        back_populates="project"
    )
    models: Mapped[list[DatabaseCapellaModel]] = relationship(
        back_populates="project"
    )
