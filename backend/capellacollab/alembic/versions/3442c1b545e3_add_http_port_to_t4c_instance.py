# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add http port to t4c instance

Revision ID: 3442c1b545e3
Revises: c6d27bd8cf6e
Create Date: 2023-06-26 17:04:34.613373

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3442c1b545e3"
down_revision = "c6d27bd8cf6e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "t4c_instances", sa.Column("http_port", sa.Integer(), nullable=True)
    )
