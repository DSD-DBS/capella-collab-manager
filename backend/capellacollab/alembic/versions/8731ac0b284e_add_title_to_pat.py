# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add title to PAT

Revision ID: 8731ac0b284e
Revises: 7b7145600133
Create Date: 2025-02-04 16:01:41.279644

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8731ac0b284e"
down_revision = "7b7145600133"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "basic_auth_token",
        sa.Column(
            "title",
            sa.String(),
            nullable=False,
            server_default=sa.text("'Legacy Token'"),
        ),
    )
