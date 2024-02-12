# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import typing as t

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import orm

# Import required for sqlalchemy
from capellacollab.core import database
from capellacollab.projects.users import models as project_users_models

if t.TYPE_CHECKING:
    from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
    from capellacollab.projects.users.models import ProjectUserAssociation


class UserMetadata(BaseModel):
    leads: int = Field(
        description="The number of users with the manager role in a project"
    )
    contributors: int = Field(
        description="The number of non-manager users with write access in a project"
    )
    subscribers: int = Field(
        description="The number of non-manager users with read access in a project"
    )


class Visibility(enum.Enum):
    PRIVATE = "private"
    INTERNAL = "internal"


class ProjectType(enum.Enum):
    GENERAL = "general"
    TRAINING = "training"


class Project(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        description="The name of a project",
        examples=["Automated Coffee Experiences"],
        max_length=255,
    )
    slug: str = Field(
        description="The slug derived from the name of a project",
        examples=["automated-coffee-experiences"],
    )
    description: str | None = Field(
        default=None,
        description="The description of a project",
        examples=["Models for exploring automated coffee experiences."],
    )
    visibility: Visibility = Field(
        description="The visibility of a project to users within the Collab Manager",
        examples=["private"],
    )
    type: ProjectType = Field(
        description="The type of project (general or training)",
        examples=["general"],
    )
    users: UserMetadata = Field(
        description="The metadata of users in a project",
        examples=[{"leads": 1, "contributors": 2, "subscribers": 3}],
    )
    is_archived: bool = Field(
        description="The archive status of a project", examples=[False]
    )

    @field_validator("users", mode="before")
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


class PatchProject(BaseModel):
    name: str | None = Field(
        default=None,
        description="The name of a project provided for patching",
        examples=["Robotic Coffee Experiences"],
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        description="The description of a project provided for patching",
        examples=["Models for exploring robotic coffee experiences."],
        max_length=1500,
    )
    visibility: Visibility | None = Field(
        default=None,
        description="The visibility of a project provided for patching",
        examples=["private"],
    )
    type: ProjectType | None = Field(
        default=None,
        description="The type of project (general or training) provided for patching",
        examples=["private"],
    )
    is_archived: bool | None = Field(
        default=None,
        description="The archive status of a project provided for patching",
        examples=[True],
    )


class PostProjectRequest(BaseModel):
    name: str = Field(
        description="The name of a project provided at creation",
        examples=["Automated Coffee Experiences"],
        max_length=255,
    )
    description: str | None = Field(
        default=None,
        description="The description of a project provided at creation",
        examples=["Models for exploring automated coffee experiences."],
        max_length=1500,
    )
    visibility: Visibility = Field(
        default=Visibility.PRIVATE,
        description="The visibility of a project provided at creation",
        examples=["private"],
    )


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
