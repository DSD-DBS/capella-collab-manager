# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove RDP Username

Revision ID: 1b4c1dc944d6
Revises: d3c85f34aae6
Create Date: 2021-08-26 16:41:03.205051

"""
# 3rd party:
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1b4c1dc944d6"
down_revision = "d3c85f34aae6"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("sessions", "rdp_username")


def downgrade():
    op.add_column(
        "sessions",
        sa.Column("rdp_username", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
