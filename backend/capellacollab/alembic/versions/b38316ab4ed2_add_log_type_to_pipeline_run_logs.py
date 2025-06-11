# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add log_type to pipeline run logs

Revision ID: b38316ab4ed2
Revises: 5c2b67186e66
Create Date: 2025-06-13 16:46:30.015631

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b38316ab4ed2"
down_revision = "5c2b67186e66"
branch_labels = None
depends_on = None


def upgrade():
    sa.Enum("EVENTS", "LOGS", name="logtype").create(op.get_bind())
    op.add_column(
        "pipeline_run_logs",
        sa.Column(
            "log_type",
            postgresql.ENUM(
                "EVENTS", "LOGS", name="logtype", create_type=False
            ),
            nullable=False,
        ),
    )
