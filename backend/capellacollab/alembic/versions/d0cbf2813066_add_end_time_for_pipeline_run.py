# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add end_time for pipeline run

Revision ID: d0cbf2813066
Revises: 90abdec3827e
Create Date: 2023-07-26 18:16:55.723944

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d0cbf2813066"
down_revision = "90abdec3827e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pipeline_run", sa.Column("end_time", sa.DateTime(), nullable=True)
    )
