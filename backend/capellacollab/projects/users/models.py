# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import enum
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
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


class ProjectUser(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    role: ProjectUserRole
    permission: ProjectUserPermission
    user: users_models.User


class PostProjectUser(pydantic.BaseModel):
    role: ProjectUserRole
    permission: ProjectUserPermission
    username: str
    reason: str


class PatchProjectUser(pydantic.BaseModel):
    role: ProjectUserRole | None = None
    permission: ProjectUserPermission | None = None
    reason: str


class ProjectUserAssociation(database.Base):
    __tablename__ = "project_user_association"

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), primary_key=True
    )
    user: orm.Mapped["DatabaseUser"] = orm.relationship(
        back_populates="projects"
    )

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id"), primary_key=True
    )
    project: orm.Mapped["DatabaseProject"] = orm.relationship(
        back_populates="users"
    )

    permission: orm.Mapped[ProjectUserPermission]
    role: orm.Mapped[ProjectUserRole]
