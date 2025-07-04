# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add reason to log line table

Revision ID: 169c90c7eff1
Revises: b38316ab4ed2
Create Date: 2025-06-17 14:48:47.282144

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "169c90c7eff1"
down_revision = "b38316ab4ed2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pipeline_run_logs", sa.Column("reason", sa.String(), nullable=True)
    )
