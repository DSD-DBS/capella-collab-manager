# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0
import datetime
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.users.models import DatabaseUser


class UserToken(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: int
    user_id: int
    hash: str
    expiration_date: datetime.date
    description: str
    source: str


class UserTokenWithPassword(UserToken):
    password: str


class PostToken(pydantic.BaseModel):
    expiration_date: datetime.datetime
    description: str
    source: str


class DatabaseUserToken(database.Base):
    __tablename__ = "basic_auth_token"

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, autoincrement=True
    )
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("users.id"))
    user: orm.Mapped["DatabaseUser"] = orm.relationship(
        back_populates="tokens", foreign_keys=[user_id]
    )
    hash: orm.Mapped[str]
    expiration_date: orm.Mapped[datetime.date]
    description: orm.Mapped[str]
    source: orm.Mapped[str]
