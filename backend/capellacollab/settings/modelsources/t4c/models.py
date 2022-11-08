# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import enum
import logging
import typing as t

import pydantic
import requests
from pydantic import BaseModel, validator
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

from capellacollab.core.database import Base

log = logging.getLogger(__name__)


def validate_rest_api_url(value: t.Optional[str]):
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
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    version_id = Column(Integer, ForeignKey("versions.id"))
    license = Column(String)
    host = Column(String)
    port = Column(
        Integer,
        CheckConstraint("port >= 0 AND port <= 65535"),
    )
    usage_api = Column(String)
    rest_api = Column(String)
    username = Column(String)
    password = Column(String)
    protocol = Column(
        Enum(Protocol),
        nullable=False,
        default=Protocol.tcp,
    )

    version = relationship("Version")
    repositories = relationship(
        "DatabaseT4CRepository",
        back_populates="instance",
        cascade="all, delete",
    )


def latin_1_validator(value: t.Optional[str]) -> t.Optional[str]:
    if not value:
        return value
    try:
        value.encode("latin-1")
    except UnicodeEncodeError as e:
        raise ValueError("Value should only use latin-1 characters.")
    return value


class T4CInstanceBase(BaseModel):
    license: str
    host: str
    port: int
    usage_api: str
    rest_api: str
    username: str
    protocol: Protocol

    # validators
    _validate_username = validator("username", allow_reuse=True)(
        latin_1_validator
    )

    _validate_rest_api_url = pydantic.validator("rest_api", allow_reuse=True)(
        validate_rest_api_url
    )

    class Config:
        orm_mode = True


class PatchT4CInstance(BaseModel):
    license: t.Optional[str]
    host: t.Optional[str]
    port: t.Optional[int]
    usage_api: t.Optional[str]
    rest_api: t.Optional[str]
    username: t.Optional[str]
    password: t.Optional[str]
    protocol: t.Optional[Protocol]

    # validators
    _validate_username = validator("username", allow_reuse=True)(
        latin_1_validator
    )

    _validate_password = validator("password", allow_reuse=True)(
        latin_1_validator
    )

    _validate_rest_api_url = pydantic.validator("rest_api", allow_reuse=True)(
        validate_rest_api_url
    )

    class Config:
        orm_mode = True


class T4CInstanceComplete(T4CInstanceBase):
    name: str
    version_id: int


class CreateT4CInstance(T4CInstanceComplete):
    password: str

    # validators
    _validate_password = validator("password", allow_reuse=True)(
        latin_1_validator
    )


class Version(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class T4CInstance(T4CInstanceComplete):
    id: int
    version: Version
