# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import logging
import typing as t

import pydantic
import requests
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.tools import models as tools_models

if t.TYPE_CHECKING:
    from capellacollab.tools.models import Version

    from .repositories.models import DatabaseT4CRepository

log = logging.getLogger(__name__)


def validate_rest_api_url(value: str | None):
    if value:
        try:
            requests.Request("GET", value).prepare()
        except requests.RequestException:
            log.info("REST API Validation failed", exc_info=True)
            raise ValueError(
                "The provided TeamForCapella REST API is not valid."
            )
    return value


class Protocol(str, enum.Enum):
    tcp = "tcp"
    ssl = "ssl"
    ws = "ws"
    wss = "wss"


class DatabaseT4CInstance(database.Base):
    __tablename__ = "t4c_instances"

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, autoincrement=True
    )

    name: orm.Mapped[str]

    license: orm.Mapped[str]
    host: orm.Mapped[str]
    port: orm.Mapped[int] = orm.mapped_column(
        sa.CheckConstraint("port >= 0 AND port <= 65535"), default=2036
    )
    cdo_port: orm.Mapped[int] = orm.mapped_column(
        sa.CheckConstraint("cdo_port >= 0 AND cdo_port <= 65535"),
        default=12036,
    )
    http_port: orm.Mapped[int | None] = orm.mapped_column(
        sa.CheckConstraint("http_port >= 0 AND http_port <= 65535"),
    )
    usage_api: orm.Mapped[str]
    rest_api: orm.Mapped[str]
    username: orm.Mapped[str]
    password: orm.Mapped[str]

    protocol: orm.Mapped[Protocol] = orm.mapped_column(default=Protocol.tcp)

    version_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("versions.id")
    )
    version: orm.Mapped[Version] = orm.relationship()

    repositories: orm.Mapped[list[DatabaseT4CRepository]] = orm.relationship(
        back_populates="instance", cascade="all, delete"
    )


def port_validator(value: int | None) -> int | None:
    if not value:
        return value
    assert 0 <= value <= 65535
    return value


class T4CInstanceBase(pydantic.BaseModel):
    license: str
    host: str
    port: int
    cdo_port: int
    http_port: int | None
    usage_api: str
    rest_api: str
    username: str
    protocol: Protocol

    # validators
    _validate_rest_api_url = pydantic.validator("rest_api", allow_reuse=True)(
        validate_rest_api_url
    )

    _validate_port = pydantic.validator("port", allow_reuse=True)(
        port_validator
    )

    _validate_cdo_port = pydantic.validator("cdo_port", allow_reuse=True)(
        port_validator
    )

    _validate_http_port = pydantic.validator("http_port", allow_reuse=True)(
        port_validator
    )

    class Config:
        orm_mode = True


class PatchT4CInstance(pydantic.BaseModel):
    name: str | None
    license: str | None
    host: str | None
    port: int | None
    cdo_port: int | None
    http_port: int | None
    usage_api: str | None
    rest_api: str | None
    username: str | None
    password: str | None
    protocol: Protocol | None
    version_id: int | None

    # validators
    _validate_rest_api_url = pydantic.validator("rest_api", allow_reuse=True)(
        validate_rest_api_url
    )

    _validate_port = pydantic.validator("port", allow_reuse=True)(
        port_validator
    )

    _validate_cdo_port = pydantic.validator("cdo_port", allow_reuse=True)(
        port_validator
    )

    _validate_http_port = pydantic.validator("http_port", allow_reuse=True)(
        port_validator
    )

    class Config:
        orm_mode = True


class T4CInstanceComplete(T4CInstanceBase):
    name: str
    version_id: int


class CreateT4CInstance(T4CInstanceComplete):
    password: str


class T4CInstance(T4CInstanceComplete):
    id: int
    version: tools_models.ToolVersionBase
