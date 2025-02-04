# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add fine-grained token support

Revision ID: 7b7145600133
Revises: 4cf566b4f986
Create Date: 2024-12-18 12:04:14.280817

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "7b7145600133"
down_revision = "4cf566b4f986"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_pat_association",
        sa.Column("token_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "scope",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.ForeignKeyConstraint(
            ["token_id"],
            ["basic_auth_token.id"],
        ),
        sa.PrimaryKeyConstraint("token_id", "project_id"),
    )
    op.add_column(
        "basic_auth_token",
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "basic_auth_token",
        sa.Column(
            "scope",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )
