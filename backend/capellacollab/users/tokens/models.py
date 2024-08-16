# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import datetime
import enum
import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic

if t.TYPE_CHECKING:
    from capellacollab.users.models import DatabaseUser


class UserToken(core_pydantic.BaseModel):
    id: int
    user_id: int
    hash: str
    expiration_date: datetime.date
    description: str
    source: str


class UserTokenResource(str, enum.Enum):
    OWN_SESSIONS = "own_sessions"


class UserTokenVerb(str, enum.Enum):
    GET = "GET"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class UserTokenWithPassword(UserToken):
    password: str


class PostToken(core_pydantic.BaseModel):
    expiration_date: datetime.date
    description: str
    source: str
    scopes: list[tuple[UserTokenResource, set[UserTokenVerb]]]


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
    description: orm.Mapped[str]
    source: orm.Mapped[str]
