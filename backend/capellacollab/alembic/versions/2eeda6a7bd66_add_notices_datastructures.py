# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add notices datastructures

Revision ID: 2eeda6a7bd66
Revises: 279ec954b302
Create Date: 2021-08-23 14:05:20.897134

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2eeda6a7bd66"
down_revision = "279ec954b302"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "notices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column(
            "level",
            sa.Enum(
                "PRIMARY",
                "SECONDARY",
                "SUCCESS",
                "DANGER",
                "WARNING",
                "INFO",
                "ALERT",
                name="noticelevel",
            ),
            nullable=True,
        ),
        sa.Column("scope", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notices_id"), "notices", ["id"], unique=False)
