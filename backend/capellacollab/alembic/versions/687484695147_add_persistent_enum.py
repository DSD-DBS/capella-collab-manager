# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add Persistent Enum

Revision ID: 687484695147
Revises: e23ab83c2195
Create Date: 2021-10-07 15:09:50.518254

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "687484695147"
down_revision = "d7fe491603c3"
branch_labels = None
depends_on = None


def upgrade():
    workspacetype = postgresql.ENUM(
        "PERSISTENT", "READONLY", name="workspacetype"
    )
    workspacetype.create(op.get_bind())
    op.add_column(
        "sessions",
        sa.Column(
            "type",
            sa.Enum("PERSISTENT", "READONLY", name="workspacetype"),
            nullable=False,
            server_default="PERSISTENT",
        ),
    )
