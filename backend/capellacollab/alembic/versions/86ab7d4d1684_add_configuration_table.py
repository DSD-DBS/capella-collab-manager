# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add configuration table

Revision ID: 86ab7d4d1684
Revises: f55b41e32223
Create Date: 2023-10-27 14:54:40.452599

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "86ab7d4d1684"
down_revision = "f55b41e32223"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "configuration",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "configuration",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_configuration_id"), "configuration", ["id"], unique=True
    )
    op.create_index(
        op.f("ix_configuration_name"), "configuration", ["name"], unique=True
    )
