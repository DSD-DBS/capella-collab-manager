# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.core import pydantic as core_pydantic
from capellacollab.users import models as users_models


class Workspace(core_pydantic.BaseModel):
    id: int
    pvc_name: str
    size: str


class DatabaseWorkspace(database.Base):
    __tablename__ = "workspaces"

    id: orm.Mapped[int] = orm.mapped_column(
        init=False, primary_key=True, index=True, autoincrement=True
    )

    pvc_name: orm.Mapped[str] = orm.mapped_column(unique=True)
    size: orm.Mapped[str]

    user_id: orm.Mapped[int] = orm.mapped_column(
        sa.ForeignKey("users.id"), primary_key=True, init=False
    )
    user: orm.Mapped[users_models.DatabaseUser] = orm.relationship()
