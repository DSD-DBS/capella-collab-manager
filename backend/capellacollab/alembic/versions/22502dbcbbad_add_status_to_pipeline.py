# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add status to pipeline

Revision ID: 22502dbcbbad
Revises: 08912d599912
Create Date: 2023-02-25 20:21:06.080728

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "22502dbcbbad"
down_revision = "08912d599912"
branch_labels = None
depends_on = None


def upgrade():
    protocol = sa.Enum(
        "PENDING",
        "SCHEDULED",
        "RUNNING",
        "SUCCESS",
        "TIMEOUT",
        "FAILURE",
        "UNKNOWN",
        name="pipelinerunstatus",
    )
    protocol.create(op.get_bind())
    op.add_column(
        "pipeline_run",
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
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("pipeline_run", "status")
    op.execute("DROP TYPE pipelinerunstatus")
