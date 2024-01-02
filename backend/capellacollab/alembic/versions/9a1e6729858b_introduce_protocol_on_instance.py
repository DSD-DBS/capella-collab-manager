# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Introduce protocol on instance.

Revision ID: 9a1e6729858b
Revises: e7a140389e22
Create Date: 2022-11-08 10:06:04.740051

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9a1e6729858b"
down_revision = "8eceebe9b3ea"
branch_labels = None
depends_on = None


def upgrade():
    protocol = sa.Enum("tcp", "ssl", "ws", "wss", name="protocol")
    protocol.create(op.get_bind())
    op.add_column(
        "t4c_instances",
        sa.Column("protocol", protocol, server_default="tcp", nullable=False),
    )
