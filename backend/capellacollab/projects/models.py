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


class ProjectType(enum.Enum):
    GENERAL = "general"
    TRAINING = "training"


class Project(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str
    slug: str
    description: str | None = None
    visibility: Visibility
    type: ProjectType
    users: UserMetadata
    is_archived: bool

    @pydantic.field_validator("users", mode="before")
    @classmethod
    def transform_users(cls, data: t.Any):
        if isinstance(data, UserMetadata):
            return data

        if isinstance(data, list):
            # Assumption: If it is a list, all entries are of type ProjectUserAssociation
            return UserMetadata(
                leads=len(
                    [
                        user
                        for user in data
                        if user.role
                        == project_users_models.ProjectUserRole.MANAGER
                    ]
                ),
                contributors=len(
                    [
                        user
                        for user in data
                        if user.role
                        == project_users_models.ProjectUserRole.USER
                        and user.permission
                        == project_users_models.ProjectUserPermission.WRITE
                    ]
                ),
                subscribers=len(
                    [
                        user
                        for user in data
                        if user.role
                        == project_users_models.ProjectUserRole.USER
                        and user.permission
                        == project_users_models.ProjectUserPermission.READ
                    ]
                ),
            )

        return data


class PatchProject(pydantic.BaseModel):
    name: str | None = None
    description: str | None = None
    visibility: Visibility | None = None
    type: ProjectType | None = None
    is_archived: bool | None = None


class PostProjectRequest(pydantic.BaseModel):
    name: str
    description: str | None = None
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
    type: orm.Mapped[ProjectType]

    users: orm.Mapped[list[ProjectUserAssociation]] = orm.relationship(
        back_populates="project"
    )
    models: orm.Mapped[list[DatabaseCapellaModel]] = orm.relationship(
        back_populates="project"
    )

    is_archived: orm.Mapped[bool] = orm.mapped_column(default=False)
