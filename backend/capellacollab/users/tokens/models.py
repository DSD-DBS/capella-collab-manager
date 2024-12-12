# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import datetime
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.core.database import decorator as database_decorator
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    models as project_permissions_models,
)

if t.TYPE_CHECKING:
    from capellacollab.projects.permissions.models import (
        DatabaseProjectPATAssociation,
    )
    from capellacollab.users.models import DatabaseUser


class FineGrainedResource(core_pydantic.BaseModel):
    user: permissions_models.UserScopes = pydantic.Field(
        default_factory=permissions_models.UserScopes
    )
    admin: permissions_models.AdminScopes = pydantic.Field(
        default_factory=permissions_models.AdminScopes
    )
    projects: dict[str, project_permissions_models.ProjectUserScopes] = (
        pydantic.Field(
            default_factory=dict,
            description="Project Slug / Resource mapping.",
        )
    )


class UserToken(core_pydantic.BaseModel):
    id: int
    user_id: int
    expiration_date: datetime.date
    requested_scopes: FineGrainedResource = pydantic.Field(
        description="The scope the token was requested for."
    )
    actual_scopes: FineGrainedResource = pydantic.Field(
        description="The actual scope of the token. It might be less than the requested scope."
    )
    created_at: datetime.datetime | None
    description: str
    source: str

    _validate_created_at = pydantic.field_serializer("created_at")(
        core_pydantic.datetime_serializer_optional
    )


class UserTokenWithPassword(UserToken):
    password: str


class PostToken(core_pydantic.BaseModel):
    expiration_date: datetime.date
    description: str
    source: str
    scopes: FineGrainedResource


class DatabaseUserToken(database.Base):
    __tablename__ = "basic_auth_token"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )
    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), init=False
    )
    user: orm.Mapped["DatabaseUser"] = orm.relationship(
        back_populates="tokens", foreign_keys=[user_id]
    )
    hash: orm.Mapped[str]
    expiration_date: orm.Mapped[datetime.date]
    created_at: orm.Mapped[datetime.datetime | None]
    description: orm.Mapped[str]
    source: orm.Mapped[str]

    scope: orm.Mapped[permissions_models.GlobalScopes] = orm.mapped_column(
        database_decorator.PydanticDecorator(permissions_models.GlobalScopes),
    )
    project_scopes: orm.Mapped[list["DatabaseProjectPATAssociation"]] = (
        orm.relationship(
            default_factory=list,
            back_populates="token",
            cascade="all, delete-orphan",
        )
    )
