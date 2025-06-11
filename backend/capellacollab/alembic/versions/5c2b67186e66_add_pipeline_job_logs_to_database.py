# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add pipeline job logs to database

Revision ID: 5c2b67186e66
Revises: 44b3af069228
Create Date: 2025-06-12 16:24:21.381537

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5c2b67186e66"
down_revision = "44b3af069228"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pipeline_run_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.Integer(), nullable=False),
        sa.Column("line", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["pipeline_run.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pipeline_run_logs_run_id"),
        "pipeline_run_logs",
        ["run_id"],
        unique=False,
    )
    op.add_column(
        "pipeline_run",
        sa.Column("logs_last_timestamp", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "pipeline_run",
        sa.Column(
            "events_last_fetched_timestamp", sa.DateTime(), nullable=True
        ),
    )
