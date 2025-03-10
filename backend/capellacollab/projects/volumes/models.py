# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects import models as projects_models


class ProjectVolume(core_pydantic.BaseModel):
    id: int
    created_at: datetime.datetime
    size: str
    pvc_name: str

    _validate_created_at = pydantic.field_serializer("created_at")(
        core_pydantic.datetime_serializer
    )


class DatabaseProjectVolume(database.Base):
    __tablename__ = "project_volumes"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    created_at: orm.Mapped[datetime.datetime]
    pvc_name: orm.Mapped[str] = orm.mapped_column(unique=True)
    size: orm.Mapped[str]

    project_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("projects.id"), init=False
    )
    project: orm.Mapped[projects_models.DatabaseProject] = orm.relationship()
