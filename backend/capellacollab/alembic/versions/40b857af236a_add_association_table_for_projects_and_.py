# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add association table for projects and tags

Revision ID: 40b857af236a
Revises: 3b8e034f85c9
Create Date: 2025-05-05 16:03:10.941768

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "40b857af236a"
down_revision = "3b8e034f85c9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects_tags_association",
        sa.Column("projects_id", sa.Integer(), nullable=False),
        sa.Column("tags_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["projects_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tags_id"],
            ["tags.id"],
        ),
        sa.PrimaryKeyConstraint("projects_id", "tags_id"),
    )
