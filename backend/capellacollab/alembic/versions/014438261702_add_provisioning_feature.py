# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add provisioning feature

Revision ID: 014438261702
Revises: 320c5b39c509
Create Date: 2024-10-11 17:34:05.210906

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "014438261702"
down_revision = "320c5b39c509"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "model_provisioning",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tool_model_id", sa.Integer(), nullable=False),
        sa.Column("revision", sa.String(), nullable=False),
        sa.Column("commit_hash", sa.String(), nullable=False),
        sa.Column("provisioned_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tool_model_id"],
            ["models.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_model_provisioning_id"),
        "model_provisioning",
        ["id"],
        unique=False,
    )
    op.add_column(
        "sessions", sa.Column("provisioning_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "sessions", "model_provisioning", ["provisioning_id"], ["id"]
    )
