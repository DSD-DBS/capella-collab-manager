# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import typing as t

import pydantic
from sqlalchemy import orm

from capellacollab.core import database


class DatabaseConfiguration(database.Base):
    __tablename__ = "configuration"

    id: orm.Mapped[int] = orm.mapped_column(
        unique=True, primary_key=True, index=True
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True, index=True)
    configuration: orm.Mapped[dict[str, t.Any]]


class CPUCostConfiguration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    reserved: float | None = pydantic.Field(
        default=None,
        description="CPU reserved costs per mCore / hour",
    )
    burst: float | None = pydantic.Field(
        default=None, description="CPU burst costs per mCore / hour"
    )


class MemoryCostConfiguration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    reserved: float | None = pydantic.Field(
        default=None, description="Memory reserved costs per MiB / hour"
    )
    burst: float | None = pydantic.Field(
        default=None, description="Memory burst costs per MiB / hour"
    )


class SessionsCostConfiguration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    cpu: CPUCostConfiguration = pydantic.Field(default=CPUCostConfiguration())
    memory: MemoryCostConfiguration = pydantic.Field(
        default=MemoryCostConfiguration()
    )
    storage: float | None = pydantic.Field(
        default=None, description="Storage costs per GiB / month"
    )
    currency: str = pydantic.Field(default="€", min_length=1, max_length=5)


class SessionsConfiguration(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    costs: SessionsCostConfiguration = pydantic.Field(
        default=SessionsCostConfiguration()
    )


class ConfigurationBase(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")

    _name: str


class GlobalConfiguration(ConfigurationBase):
    """Global application configuration."""

    _name = "global"

    sessions: SessionsConfiguration = pydantic.Field(
        default=SessionsConfiguration()
    )
