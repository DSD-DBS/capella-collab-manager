# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.users import models as users_models

if t.TYPE_CHECKING:
    from capellacollab.projects.models import DatabaseProject
    from capellacollab.users.models import DatabaseUser


class ProjectUserRole(enum.Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "administrator"


class ProjectUserPermission(enum.Enum):
    READ = "read"
    WRITE = "write"


class ProjectUser(core_pydantic.BaseModel):
    role: ProjectUserRole
    permission: ProjectUserPermission
    user: users_models.User


class PostProjectUser(core_pydantic.BaseModel):
    role: ProjectUserRole = pydantic.Field(
        description=(
            "The role of the user in the project. "
            "Can be 'user' or 'manager'. Manager is also referred "
            "to as project administrator in the documentation."
        )
    )
    permission: ProjectUserPermission
    username: str
    reason: str


class PatchProjectUser(core_pydantic.BaseModel):
    role: ProjectUserRole | None = None
    permission: ProjectUserPermission | None = None
    reason: str


class ProjectUserAssociation(database.Base):
    __tablename__ = "project_user_association"

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), primary_key=True, init=False
    )
    user: orm.Mapped["DatabaseUser"] = orm.relationship(
        back_populates="projects"
    )

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id"), primary_key=True, init=False
    )
    project: orm.Mapped["DatabaseProject"] = orm.relationship(
        back_populates="users"
    )

    permission: orm.Mapped[ProjectUserPermission]
    role: orm.Mapped[ProjectUserRole]
