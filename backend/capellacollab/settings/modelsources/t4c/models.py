# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import enum
import logging
import typing as t

import pydantic
import requests
from pydantic import BaseModel
from requests.exceptions import RequestException
from sqlalchemy import (
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

import capellacollab.tools.models as tools_models
from capellacollab.core.database import Base

if t.TYPE_CHECKING:
    from .repositories.models import DatabaseT4CRepository

log = logging.getLogger(__name__)


def validate_rest_api_url(value: str | None):
    if value:
        try:
            requests.Request("GET", value).prepare()
        except RequestException:
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


class DatabaseT4CInstance(Base):
    __tablename__ = "t4c_instances"
    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String, nullable=False)
    version_id: int = Column(Integer, ForeignKey("versions.id"))
    license: str = Column(String)
    host: str = Column(String)
    port: int = Column(
        Integer,
        CheckConstraint("port >= 0 AND port <= 65535"),
        nullable=False,
        default=2036,
    )
    cdo_port: int = Column(
        Integer,
        CheckConstraint("cdo_port >= 0 AND cdo_port <= 65535"),
        nullable=False,
        default=12036,
    )
    usage_api: str = Column(String)
    rest_api: str = Column(String)
    username: str = Column(String)
    password: str = Column(String)
    protocol: Protocol = Column(
        Enum(Protocol),
        nullable=False,
        default=Protocol.tcp,
    )

    version: tools_models.Version = relationship(tools_models.Version)
    repositories: list[DatabaseT4CRepository] = relationship(
        "DatabaseT4CRepository",
        back_populates="instance",
        cascade="all, delete",
    )


def port_validator(value: int | None) -> int | None:
    if not value:
        return value
    assert 0 <= value <= 65535
    return value


class T4CInstanceBase(BaseModel):
    license: str
    host: str
    port: int
    cdo_port: int
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

    class Config:
        orm_mode = True


class FieldsT4CInstance(BaseModel):
    license: str | None
    host: str | None
    port: int | None
    cdo_port: int | None
    usage_api: str | None
    rest_api: str | None
    username: str | None
    password: str | None
    protocol: Protocol | None

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

    class Config:
        orm_mode = True


class PatchT4CInstance(FieldsT4CInstance):
    version_id: int | None


class T4CInstanceComplete(T4CInstanceBase):
    name: str
    version_id: int


class CreateT4CInstance(T4CInstanceComplete):
    password: str


class Version(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class T4CInstance(T4CInstanceComplete):
    id: int
    version: Version
