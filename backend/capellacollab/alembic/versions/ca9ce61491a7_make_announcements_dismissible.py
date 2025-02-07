# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Make announcements dismissible

Revision ID: ca9ce61491a7
Revises: 16a64401737c
Create Date: 2025-02-07 19:42:01.723097

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ca9ce61491a7"
down_revision = "16a64401737c"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("notices", "announcements")

    op.add_column(
        "announcements", sa.Column("dismissible", sa.Boolean(), nullable=True)
    )
    op.execute("UPDATE announcements SET dismissible = false")
    op.alter_column("announcements", "dismissible", nullable=False)
