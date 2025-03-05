# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add managed field to personal access token

Revision ID: db35c7cfb407
Revises: ca9ce61491a7
Create Date: 2025-03-05 11:29:55.134734

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "db35c7cfb407"
down_revision = "ca9ce61491a7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "basic_auth_token",
        sa.Column(
            "managed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
