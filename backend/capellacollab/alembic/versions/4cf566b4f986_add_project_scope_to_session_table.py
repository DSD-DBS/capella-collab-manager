# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add project scope to session table

Revision ID: 4cf566b4f986
Revises: 2f8449c217fa
Create Date: 2024-12-02 14:40:15.815359

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4cf566b4f986"
down_revision = "2f8449c217fa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions", sa.Column("project_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, "sessions", "projects", ["project_id"], ["id"])
