# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database


class DatabaseUserTokenModel(database.Base):
    __tablename__ = "basic_auth_token"

    id: orm.Mapped[int] = orm.mapped_column(
        primary_key=True, index=True, autoincrement=True
    )
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey("users.id"))
    hash: orm.Mapped[str]
    expiration_date: orm.Mapped[datetime.date]
    description: orm.Mapped[str]
