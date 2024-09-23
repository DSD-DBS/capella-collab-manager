# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import logging
import typing as t

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.tools import models as tools_models

if t.TYPE_CHECKING:
    from capellacollab.settings.modelsources.t4c.instance.repositories.models import (
        DatabaseT4CRepository,
    )
    from capellacollab.settings.modelsources.t4c.license_server.models import (
        DatabaseT4CLicenseServer,
    )
    from capellacollab.tools.models import DatabaseVersion

log = logging.getLogger(__name__)


class Protocol(str, enum.Enum):
    tcp = "tcp"
    ssl = "ssl"
    ws = "ws"
    wss = "wss"


class DatabaseT4CInstance(database.Base):
    __tablename__ = "t4c_instances"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True)

    license_server_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("t4c_license_servers.id"), init=False, nullable=False
    )
    license_server: orm.Mapped[DatabaseT4CLicenseServer] = orm.relationship(
        back_populates="instances"
    )

    host: orm.Mapped[str]

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
    protocol: orm.Mapped[Protocol] = orm.mapped_column(default=Protocol.tcp)

    is_archived: orm.Mapped[bool] = orm.mapped_column(default=False)


def port_validator(value: int | None) -> int | None:
    if not value:
        return value
    assert 0 <= value <= 65535
    return value


class T4CInstanceBase(core_pydantic.BaseModel):
    host: str
    port: int
    cdo_port: int
    http_port: int | None = None
    rest_api: t.Annotated[pydantic.HttpUrl, pydantic.AfterValidator(str)]
    username: str
    protocol: Protocol

    _validate_port = pydantic.field_validator("port")(port_validator)
    _validate_cdo_port = pydantic.field_validator("cdo_port")(port_validator)
    _validate_http_port = pydantic.field_validator("http_port")(port_validator)


class PatchT4CInstance(core_pydantic.BaseModel):
    name: str | None = None
    license_server_id: int | None = None
    host: str | None = None
    port: int | None = None
    cdo_port: int | None = None
    http_port: int | None = None
    rest_api: (
        t.Annotated[pydantic.HttpUrl, pydantic.AfterValidator(str)] | None
    ) = None
    username: str | None = None
    password: str | None = None
    protocol: Protocol | None = None
    is_archived: bool | None = None

    _validate_port = pydantic.field_validator("port")(port_validator)
    _validate_cdo_port = pydantic.field_validator("cdo_port")(port_validator)
    _validate_http_port = pydantic.field_validator("http_port")(port_validator)


class T4CInstanceComplete(T4CInstanceBase):
    name: str
    version_id: int
    license_server_id: int


class CreateT4CInstance(T4CInstanceComplete):
    is_archived: bool | None = None
    password: str


class T4CInstance(T4CInstanceComplete):
    id: int
    version: tools_models.ToolVersion
    is_archived: bool
