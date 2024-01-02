# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add configuration to toolmodels

Revision ID: 97c7acd616fc
Revises: d0cbf2813066
Create Date: 2023-08-04 12:05:53.846434

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "97c7acd616fc"
down_revision = "d0cbf2813066"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "models",
        sa.Column(
            "configuration",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
