# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add user events

Revision ID: 2df2e0fd7774
Revises: 16398dfaeef7
Create Date: 2022-12-28 16:56:43.714914

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2df2e0fd7774"
down_revision = "16398dfaeef7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "created",
            sa.DateTime(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "last_login",
            sa.DateTime(),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.create_table(
        "user_history_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            "executor_id", sa.Integer(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "project_id", sa.Integer(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "execution_time",
            sa.DateTime(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "event_type",
            sa.Enum(
                "CREATED_USER",
                "ADDED_TO_PROJECT",
                "REMOVED_FROM_PROJECT",
                "ASSIGNED_PROJECT_ROLE_USER",
                "ASSIGNED_PROJECT_ROLE_MANAGER",
                "ASSIGNED_PROJECT_PERMISSION_READ_ONLY",
                "ASSIGNED_PROJECT_PERMISSION_READ_WRITE",
                "ASSIGNED_ROLE_ADMIN",
                "ASSIGNED_ROLE_USER",
                name="eventtype",
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("reason", sa.String(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["executor_id"],
            ["users.id"],
            name="user_history_events_executor_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="user_history_events_project_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="user_history_events_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="user_history_events_pkey"),
    )
    op.create_index(
        "ix_user_history_events_id",
        "user_history_events",
        ["id"],
        unique=False,
    )
