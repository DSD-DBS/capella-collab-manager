# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add run layer for pipelines

Revision ID: c6d27bd8cf6e
Revises: d1414756738a
Create Date: 2023-06-22 09:12:10.587478

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c6d27bd8cf6e"
down_revision = "d1414756738a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pipeline_run",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_id", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "SCHEDULED",
                "RUNNING",
                "SUCCESS",
                "TIMEOUT",
                "FAILURE",
                "UNKNOWN",
                name="pipelinerunstatus",
            ),
            nullable=False,
        ),
        sa.Column("pipeline_id", sa.Integer(), nullable=False),
        sa.Column("triggerer_id", sa.Integer(), nullable=False),
        sa.Column("trigger_time", sa.DateTime(), nullable=False),
        sa.Column("logs_last_fetched_timestamp", sa.DateTime(), nullable=True),
        sa.Column(
            "environment",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["pipeline_id"],
            ["backups.id"],
        ),
        sa.ForeignKeyConstraint(
            ["triggerer_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pipeline_run_id"), "pipeline_run", ["id"], unique=False
    )
