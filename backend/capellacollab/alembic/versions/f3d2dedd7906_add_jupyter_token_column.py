# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add column for Jupyter token

Revision ID: f3d2dedd7906
Revises: 4df9c82766e2
Create Date: 2023-02-03 14:31:55.776520

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f3d2dedd7906"
down_revision = "f7c1a89af5d7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions", sa.Column("jupyter_token", sa.String(), nullable=True)
    )
