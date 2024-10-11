# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add project tools table

Revision ID: 2f8449c217fa
Revises: 014438261702
Create Date: 2024-10-29 14:11:47.774679

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2f8449c217fa"
down_revision = "014438261702"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_tool_association",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("tool_version_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tool_version_id"],
            ["versions.id"],
        ),
        sa.PrimaryKeyConstraint("id", "project_id", "tool_version_id"),
    )
