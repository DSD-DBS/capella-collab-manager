# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add link between tags and users

Revision ID: 44b3af069228
Revises: a64ede3cfbb2
Create Date: 2025-05-13 17:56:02.741591

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "44b3af069228"
down_revision = "a64ede3cfbb2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users_tags_association",
        sa.Column("users_id", sa.Integer(), nullable=False),
        sa.Column("tags_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tags_id"],
            ["tags.id"],
        ),
        sa.ForeignKeyConstraint(
            ["users_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("users_id", "tags_id"),
    )
