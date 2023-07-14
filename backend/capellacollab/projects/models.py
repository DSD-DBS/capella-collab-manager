# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

import pydantic
from sqlalchemy import orm

# Import required for sqlalchemy
from capellacollab.core import database
from capellacollab.projects.users import models as project_users_models

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
    from capellacollab.projects.users.models import ProjectUserAssociation


class UserMetadata(pydantic.BaseModel):
    leads: int
    contributors: int
    subscribers: int


class Visibility(enum.Enum):
    PRIVATE = "private"
    INTERNAL = "internal"


class Project(pydantic.BaseModel):
    name: str
    slug: str
    description: str | None
    visibility: Visibility
    users: UserMetadata

    @pydantic.validator("users", pre=True)
    @classmethod
    def transform_users(
        cls,
        users: UserMetadata
        | list[project_users_models.ProjectUserAssociation],
    ):
        if isinstance(users, (UserMetadata, dict)):
            return users

        return UserMetadata(
            leads=len(
                [
                    user
                    for user in users
                    if user.role
                    == project_users_models.ProjectUserRole.MANAGER
                ]
            ),
            contributors=len(
                [
                    user
                    for user in users
                    if user.role == project_users_models.ProjectUserRole.USER
                    and user.permission
                    == project_users_models.ProjectUserPermission.WRITE
                ]
            ),
            subscribers=len(
                [
                    user
                    for user in users
                    if user.role == project_users_models.ProjectUserRole.USER
                    and user.permission
                    == project_users_models.ProjectUserPermission.READ
                ]
            ),
        )

    class Config:
        orm_mode = True


class PatchProject(pydantic.BaseModel):
    name: str | None
    description: str | None
    visibility: Visibility | None


class PostProjectRequest(pydantic.BaseModel):
    name: str
    description: str | None
    visibility: Visibility = Visibility.PRIVATE


class DatabaseProject(database.Base):
    __tablename__ = "projects"

    id: orm.Mapped[int] = orm.mapped_column(
        unique=True, primary_key=True, index=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    slug: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    description: orm.Mapped[str | None]
    visibility: orm.Mapped[Visibility]

    users: orm.Mapped[list[ProjectUserAssociation]] = orm.relationship(
        back_populates="project"
    )
    models: orm.Mapped[list[DatabaseCapellaModel]] = orm.relationship(
        back_populates="project"
    )
