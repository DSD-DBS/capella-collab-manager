# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add user-determined display order to models

Revision ID: 0e2028f83156
Revises: ac0e6e0f77ee
Create Date: 2023-11-12 14:47:12.295103

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0e2028f83156"
down_revision = "ac0e6e0f77ee"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "models", sa.Column("display_order", sa.Integer(), nullable=True)
    )
