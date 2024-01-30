# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pydantic
from sqlalchemy import orm

from capellacollab.core import database


class PolarionInstance(pydantic.BaseModel):
    name: str
    url: str


class DatabasePolarionInstance(database.Base):
    __tablename__ = "polarion_instances"

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, autoincrement=True
    )
    name: orm.Mapped[str]
    url: orm.Mapped[str]
