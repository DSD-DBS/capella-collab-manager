# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add session sharing

Revision ID: 49f51db92903
Revises: aa88e6d1333b
Create Date: 2024-05-29 14:25:34.801756

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "49f51db92903"
down_revision = "aa88e6d1333b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "shared_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id", "session_id", "user_id"),
    )
    op.create_index(
        op.f("ix_shared_sessions_id"), "shared_sessions", ["id"], unique=True
    )
