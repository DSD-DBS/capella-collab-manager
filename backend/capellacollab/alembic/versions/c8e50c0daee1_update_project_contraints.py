# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


"""Add project attributes

Revision ID: c8e50c0daee1
Revises: 04482e6f1795
Create Date: 2022-05-09 15:07:16.515720

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c8e50c0daee1"
down_revision = "19a2ff65e57a"
branch_labels = None
depends_on = None


def upgrade():
    # Add description, editing_mode and project_type to project table

    op.add_column(
        "projects",
        sa.Column(
            "description", sa.String(), nullable=True, server_default=""
        ),
    )
