# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import datetime
import typing as t

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import orm

from capellacollab.core import database

if t.TYPE_CHECKING:
    from capellacollab.users.models import DatabaseUser


class UserToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="The ID of the token")
    user_id: int = Field(description="The user ID of the token creator")
    hash: str = Field(
        description="The automatically generated hash of the token"
    )
    expiration_date: datetime.date = Field(
        description="The user-provided expiration date of the token",
        examples=["2022-01-01"],
    )
    description: str = Field(
        description="The user-provided description of the token",
        examples=["Weekly automations"],
    )
    source: str


class UserTokenWithPassword(UserToken):
    password: str = Field(
        description="The static token password generated at token creation",
        examples=["collabmanager_1234567890"],
    )


class PostToken(BaseModel):
    expiration_date: datetime.datetime = Field(
        description="The expiration date of the token provided at creation",
        examples=["2022-01-01"],
    )
    description: str = Field(
        description="The description of the token provided at creation",
        examples=["Weekly automations"],
    )
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
