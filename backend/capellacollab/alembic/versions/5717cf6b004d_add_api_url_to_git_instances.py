# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add api_url to git instances

Revision ID: 5717cf6b004d
Revises: 4df9c82766e2
Create Date: 2023-02-02 09:05:00.727519

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "5717cf6b004d"
down_revision = "4df9c82766e2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "git_settings", sa.Column("api_url", sa.String(), nullable=True)
    )
