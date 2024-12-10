# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add run_nighly and include_commit_history attributes

Revision ID: df07aad6525d
Revises: fcf5d69d7bbc
Create Date: 2022-11-07 14:42:40.129037

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "df07aad6525d"
down_revision = "fcf5d69d7bbc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "backups",
        sa.Column(
            "include_commit_history",
            sa.Boolean(),
            nullable=True,
            server_default="false",
        ),
    )
    op.add_column(
        "backups",
        sa.Column(
            "run_nightly", sa.Boolean(), nullable=True, server_default="true"
        ),
    )
