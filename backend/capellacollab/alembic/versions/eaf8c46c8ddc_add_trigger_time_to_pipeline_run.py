# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add trigger time to pipeline run

Revision ID: eaf8c46c8ddc
Revises: 22502dbcbbad
Create Date: 2023-02-25 22:40:22.637225

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "eaf8c46c8ddc"
down_revision = "22502dbcbbad"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pipeline_run",
        sa.Column("trigger_time", sa.TIMESTAMP(), nullable=True),
    )


def downgrade():
    op.drop_column("pipeline_run", "trigger_time")
