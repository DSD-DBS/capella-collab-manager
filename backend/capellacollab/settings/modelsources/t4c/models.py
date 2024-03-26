# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
from capellacollab.core import pydantic as core_pydantic
from capellacollab.tools import models as tools_models

if t.TYPE_CHECKING:
    from capellacollab.tools.models import DatabaseVersion

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


class GetSessionUsageResponse(core_pydantic.BaseModel):
    free: int
    total: int


class Protocol(str, enum.Enum):
    TCP = "tcp"
    SSL = "ssl"
    WS = "ws"
    WSS = "wss"


class DatabaseT4CInstance(database.Base):
    __tablename__ = "t4c_instances"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True)

    license: orm.Mapped[str]
    host: orm.Mapped[str]

    usage_api: orm.Mapped[str]
    rest_api: orm.Mapped[str]
    username: orm.Mapped[str]
    password: orm.Mapped[str]

    version_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("versions.id"), init=False
    )
    version: orm.Mapped[DatabaseVersion] = orm.relationship()

    repositories: orm.Mapped[list[DatabaseT4CRepository]] = orm.relationship(
        default_factory=list, back_populates="instance", cascade="all, delete"
    )

    port: orm.Mapped[int] = orm.mapped_column(
        sa.CheckConstraint("port >= 0 AND port <= 65535"), default=2036
    )

    http_port: orm.Mapped[int | None] = orm.mapped_column(
        sa.CheckConstraint("http_port >= 0 AND http_port <= 65535"),
        default=None,
    )
    cdo_port: orm.Mapped[int] = orm.mapped_column(
        sa.CheckConstraint("cdo_port >= 0 AND cdo_port <= 65535"),
        default=12036,
    )
    protocol: orm.Mapped[Protocol] = orm.mapped_column(default=Protocol.TCP)

    is_archived: orm.Mapped[bool] = orm.mapped_column(default=False)


def port_validator(value: int | None) -> int | None:
    if not value:
        return value
    assert 0 <= value <= 65535
    return value


class T4CInstanceBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    license: str
    host: str
    port: int
    cdo_port: int
    http_port: int | None = None
    usage_api: str
    rest_api: str
    username: str
    protocol: Protocol

    _validate_rest_api_url = pydantic.field_validator("rest_api")(
        validate_rest_api_url
    )
    _validate_port = pydantic.field_validator("port")(port_validator)
    _validate_cdo_port = pydantic.field_validator("cdo_port")(port_validator)
    _validate_http_port = pydantic.field_validator("http_port")(port_validator)


class PatchT4CInstance(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    name: str | None = None
    license: str | None = None
    host: str | None = None
    port: int | None = None
    cdo_port: int | None = None
    http_port: int | None = None
    usage_api: str | None = None
    rest_api: str | None = None
    username: str | None = None
    password: str | None = None
    protocol: Protocol | None = None
    version_id: int | None = None
    is_archived: bool | None = None

    _validate_rest_api_url = pydantic.field_validator("rest_api")(
        validate_rest_api_url
    )
    _validate_port = pydantic.field_validator("port")(port_validator)
    _validate_cdo_port = pydantic.field_validator("cdo_port")(port_validator)
    _validate_http_port = pydantic.field_validator("http_port")(port_validator)


class T4CInstanceComplete(T4CInstanceBase):
    name: str
    version_id: int


class CreateT4CInstance(T4CInstanceComplete):
    is_archived: bool | None = None
    password: str


class T4CInstance(T4CInstanceComplete):
    id: int
    version: tools_models.ToolVersionBase
    is_archived: bool
