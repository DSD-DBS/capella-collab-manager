# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add alerted columns to session

Revision ID: 01bb44cd41b4
Revises: 53b8f1f94922
Create Date: 2025-07-17 16:17:19.760356

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "01bb44cd41b4"
down_revision = "53b8f1f94922"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions",
        sa.Column(
            "alerted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
