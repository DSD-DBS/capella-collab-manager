# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add column for logs_last_fetched_timestamp

Revision ID: 04319a1afb73
Revises: eaf8c46c8ddc
Create Date: 2023-05-17 12:15:51.702106

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "04319a1afb73"
down_revision = "eaf8c46c8ddc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pipeline_run",
        sa.Column(
            "logs_last_fetched_timestamp", sa.TIMESTAMP(), nullable=True
        ),
    )


def downgrade():
    op.drop_column("pipeline_run", "logs_last_fetched_timestamp")
