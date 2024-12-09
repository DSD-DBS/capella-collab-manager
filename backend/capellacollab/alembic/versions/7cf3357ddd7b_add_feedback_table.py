# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add feedback table

Revision ID: 7cf3357ddd7b
Revises: abddaf015966
Create Date: 2024-09-30 19:47:36.253187

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7cf3357ddd7b"
down_revision = "abddaf015966"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "rating",
            sa.Enum("BAD", "OKAY", "GOOD", name="feedbackrating"),
            nullable=False,
        ),
        sa.Column("feedback_text", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("trigger", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_feedback_id"), "feedback", ["id"], unique=False)
