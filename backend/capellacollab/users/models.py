# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import datetime
import enum
import typing as t

import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

from ..permissions import models

if t.TYPE_CHECKING:
    from capellacollab.events.models import DatabaseUserHistoryEvent
    from capellacollab.projects.users.models import (
        DatabaseProjectUserAssociation,
    )
    from capellacollab.sessions.models import DatabaseSession
    from capellacollab.users.tokens.models import DatabaseUserToken


class Role(str, enum.Enum):
    ADMIN = "administrator"
    USER = "user"


USER_TOKEN_SCOPE = models.UserScopes(
    sessions={
        models.UserTokenVerb.GET,
        models.UserTokenVerb.CREATE,
        models.UserTokenVerb.UPDATE,
        models.UserTokenVerb.DELETE,
    },
    projects={models.UserTokenVerb.CREATE},
    tokens={
        models.UserTokenVerb.GET,
        models.UserTokenVerb.CREATE,
        models.UserTokenVerb.DELETE,
    },
    feedback={models.UserTokenVerb.CREATE},
)

ROLE_MAPPING = {
    Role.USER: models.GlobalScopes(
        user=USER_TOKEN_SCOPE,
    ),
    Role.ADMIN: models.GlobalScopes(
        user=USER_TOKEN_SCOPE,
        admin=models.AdminScopes(
            users={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            projects={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            tools={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            announcements={
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            monitoring={
                models.UserTokenVerb.GET,
            },
            configuration={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.UPDATE,
            },
            git_servers={
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            t4c_servers={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            t4c_repositories={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.CREATE,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            pv_configuration={
                models.UserTokenVerb.GET,
                models.UserTokenVerb.UPDATE,
                models.UserTokenVerb.DELETE,
            },
            events={
                models.UserTokenVerb.GET,
            },
            sessions={models.UserTokenVerb.GET},
            workspaces={models.UserTokenVerb.GET, models.UserTokenVerb.DELETE},
            personal_access_tokens={
                models.UserTokenVerb.DELETE,
            },
        ),
    ),
}


class BaseUser(core_pydantic.BaseModel):
    id: int
    name: str
    idp_identifier: str
    email: str | None = None
    role: Role
    beta_tester: bool = False
    blocked: bool = False


class User(BaseUser):
    created: datetime.datetime | None = None
    last_login: datetime.datetime | None = None

    _validate_created = pydantic.field_serializer("created")(
        core_pydantic.datetime_serializer_optional
    )
    _validate_last_login = pydantic.field_serializer("last_login")(
        core_pydantic.datetime_serializer_optional
    )


class PatchUser(core_pydantic.BaseModel):
    name: str | None = None
    idp_identifier: str | None = None
    email: str | None = None
    role: Role | None = None
    reason: str | None = None
    beta_tester: bool | None = None
    blocked: bool | None = None


class PostUser(core_pydantic.BaseModel):
    name: str
    idp_identifier: str
    email: str | None = None
    role: Role
    reason: str
    beta_tester: bool = False


class DatabaseUser(database.Base):
    __tablename__ = "users"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )

    idp_identifier: orm.Mapped[str] = orm.mapped_column(
        unique=True, index=True
    )
    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)

    role: orm.Mapped[Role]

    email: orm.Mapped[str | None] = orm.mapped_column(
        default=None, unique=True, index=True
    )

    created: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        default=datetime.datetime.now(datetime.UTC)
    )

    projects: orm.Mapped[list[DatabaseProjectUserAssociation]] = (
        orm.relationship(default_factory=list, back_populates="user")
    )
    sessions: orm.Mapped[list[DatabaseSession]] = orm.relationship(
        default_factory=list, back_populates="owner"
    )
    events: orm.Mapped[list[DatabaseUserHistoryEvent]] = orm.relationship(
        default_factory=list,
        back_populates="user",
        foreign_keys="DatabaseUserHistoryEvent.user_id",
    )

    tokens: orm.Mapped[list[DatabaseUserToken]] = orm.relationship(
        default_factory=list,
        back_populates="user",
        cascade="all, delete-orphan",
    )

    last_login: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        default=None
    )

    beta_tester: orm.Mapped[bool] = orm.mapped_column(default=False)
    blocked: orm.Mapped[bool] = orm.mapped_column(default=False)
