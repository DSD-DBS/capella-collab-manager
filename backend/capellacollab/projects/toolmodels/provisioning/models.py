# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import pydantic
import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.projects.toolmodels import (
    models as projects_toolmodels_models,
)
from capellacollab.sessions import models as sessions_models
from capellacollab.users import models as users_models


class ModelProvisioning(core_pydantic.BaseModel):
    session: sessions_models.Session | None
    provisioned_at: datetime.datetime
    revision: str
    commit_hash: str

    _validate_trigger_time = pydantic.field_serializer("provisioned_at")(
        core_pydantic.datetime_serializer
    )


class DatabaseModelProvisioning(database.Base):
    __tablename__ = "model_provisioning"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True
    )

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"),
        init=False,
    )
    user: orm.Mapped[users_models.DatabaseUser] = orm.relationship(
        foreign_keys=[user_id]
    )

    tool_model_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("models.id"),
        init=False,
    )
    tool_model: orm.Mapped[projects_toolmodels_models.DatabaseToolModel] = (
        orm.relationship(
            foreign_keys=[tool_model_id],
        )
    )

    revision: orm.Mapped[str]
    commit_hash: orm.Mapped[str]

    provisioned_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
    )

    session: orm.Mapped[sessions_models.DatabaseSession | None] = (
        orm.relationship(
            uselist=False, back_populates="provisioning", default=None
        )
    )
