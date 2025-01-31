# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

import pydantic
from sqlalchemy import orm

# Import required for sqlalchemy
from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.users import models as project_users_models

if t.TYPE_CHECKING:
    from capellacollab.projects.permissions.models import (
        DatabaseProjectPATAssociation,
    )
    from capellacollab.projects.toolmodels.models import DatabaseToolModel
    from capellacollab.projects.tools.models import (
        DatabaseProjectToolAssociation,
    )
    from capellacollab.projects.users.models import ProjectUserAssociation


class UserMetadata(core_pydantic.BaseModel):
    leads: int
    contributors: int
    subscribers: int


class ProjectVisibility(enum.Enum):
    PRIVATE = "private"
    INTERNAL = "internal"


class ProjectType(str, enum.Enum):
    GENERAL = "general"
    TRAINING = "training"


class Project(core_pydantic.BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    visibility: ProjectVisibility
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


class SimpleProject(core_pydantic.BaseModel):
    id: int
    name: str
    slug: str
    visibility: ProjectVisibility
    type: ProjectType


class PatchProject(core_pydantic.BaseModel):
    name: str | None = None
    description: str | None = None
    visibility: ProjectVisibility | None = None
    type: ProjectType | None = None
    is_archived: bool | None = None


class PostProjectRequest(core_pydantic.BaseModel):
    name: str
    description: str | None = None
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE
    type: ProjectType = ProjectType.GENERAL


class DatabaseProject(database.Base):
    __tablename__ = "projects"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, unique=True, primary_key=True, index=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    slug: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)

    description: orm.Mapped[str | None] = orm.mapped_column(default=None)
    visibility: orm.Mapped[ProjectVisibility] = orm.mapped_column(
        default=ProjectVisibility.PRIVATE
    )
    type: orm.Mapped[ProjectType] = orm.mapped_column(
        default=ProjectType.GENERAL
    )

    users: orm.Mapped[list[ProjectUserAssociation]] = orm.relationship(
        default_factory=list, back_populates="project"
    )
    tokens: orm.Mapped[list[DatabaseProjectPATAssociation]] = orm.relationship(
        default_factory=list,
        back_populates="project",
        cascade="all, delete-orphan",
    )
    models: orm.Mapped[list[DatabaseToolModel]] = orm.relationship(
        default_factory=list, back_populates="project"
    )
    tools: orm.Mapped[list[DatabaseProjectToolAssociation]] = orm.relationship(
        default_factory=list, back_populates="project"
    )

    is_archived: orm.Mapped[bool] = orm.mapped_column(default=False)
