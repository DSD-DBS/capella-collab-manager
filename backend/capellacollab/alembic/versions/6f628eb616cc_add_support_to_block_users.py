# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add support to block users

Revision ID: 6f628eb616cc
Revises: b2fd698ed6cb
Create Date: 2025-04-16 14:29:48.707203

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6f628eb616cc"
down_revision = "b2fd698ed6cb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "blocked",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.execute("ALTER TYPE eventtype ADD VALUE 'BLOCKED_USER'")
    op.execute("ALTER TYPE eventtype ADD VALUE 'UNBLOCKED_USER'")
