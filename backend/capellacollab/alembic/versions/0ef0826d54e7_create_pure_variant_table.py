# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Create pure::variants table

Revision ID: 0ef0826d54e7
Revises: 2df2e0fd7774
Create Date: 2022-11-18 11:40:46.395645

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0ef0826d54e7"
down_revision = "2df2e0fd7774"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pure_variants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("license_server_url", sa.String(), nullable=True),
        sa.Column("license_key_filename", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
