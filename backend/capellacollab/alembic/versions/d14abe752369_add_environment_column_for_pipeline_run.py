# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add environment column for pipeline run

Revision ID: d14abe752369
Revises: 04319a1afb73
Create Date: 2023-05-22 16:06:08.378367

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d14abe752369"
down_revision = "04319a1afb73"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pipeline_run",
        sa.Column(
            "environment",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("pipeline_run", "environment")
