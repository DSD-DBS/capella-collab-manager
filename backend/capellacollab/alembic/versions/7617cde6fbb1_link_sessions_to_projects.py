# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""link sessions to projects

Revision ID: 7617cde6fbb1
Revises: ab01ad045341
Create Date: 2022-11-10 13:13:25.041000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7617cde6fbb1"
down_revision = "ab01ad045341"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions", sa.Column("project_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, "sessions", "projects", ["project_id"], ["id"])
    op.drop_column("sessions", "repository")
