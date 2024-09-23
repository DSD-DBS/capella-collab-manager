# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import typing as t

import pydantic
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import exceptions as core_exceptions
from capellacollab.core import pydantic as core_pydantic
from capellacollab.settings.modelsources.t4c.instance import (
    models as instance_models,
)

from . import interface

if t.TYPE_CHECKING:
    from capellacollab.settings.modelsources.t4c.instance.models import (
        DatabaseT4CInstance,
    )


class DatabaseT4CLicenseServer(database.Base):
    __tablename__ = "t4c_license_servers"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False,
        primary_key=True,
        index=True,
        autoincrement=True,
        unique=True,
    )

    name: orm.Mapped[str] = orm.mapped_column(unique=True)
    usage_api: orm.Mapped[str] = orm.mapped_column()
    license_key: orm.Mapped[str] = orm.mapped_column()
    instances: orm.Mapped[list[DatabaseT4CInstance]] = orm.relationship(
        default_factory=list, back_populates="license_server"
    )


class T4CLicenseServerBase(core_pydantic.BaseModel):
    name: str
    usage_api: str
    license_key: str


class PatchT4CLicenseServer(core_pydantic.BaseModel):
    name: str | None = None
    usage_api: str | None = None
    license_key: str | None = None


class T4CLicenseServer(T4CLicenseServerBase):
    id: int
    license_server_version: str | None = None
    usage: interface.T4CLicenseServerUsage | None = None
    instances: list[instance_models.T4CInstance] = []

    @pydantic.model_validator(mode="after")
    def add_from_api(self) -> t.Any:
        self.license_server_version = interface.get_t4c_license_server_version(
            self.usage_api
        )
        try:
            self.usage = interface.get_t4c_license_server_usage(self.usage_api)
        except core_exceptions.BaseError:
            pass

        return self
