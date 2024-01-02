# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add t4c_password to sessions table

Revision ID: c3320b81a372
Revises: 9a1e6729858b
Create Date: 2022-11-09 16:50:52.026374

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "598efe35c2de"
down_revision = "c3320b81a372"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions", sa.Column("t4c_password", sa.String(), nullable=True)
    )
