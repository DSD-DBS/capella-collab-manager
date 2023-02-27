# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add pipeline runs table

Revision ID: 08912d599912
Revises: d1414756738a
Create Date: 2023-02-25 20:11:34.769429

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "08912d599912"
down_revision = "d1414756738a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pipeline_run",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("reference_id", sa.String(), nullable=True),
        sa.Column("pipeline_id", sa.Integer(), nullable=True),
        sa.Column("triggerer_id", sa.Integer(), nullable=True),
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


def downgrade():
    op.drop_index(op.f("ix_pipeline_run_id"), table_name="pipeline_run")
    op.drop_table("pipeline_run")
