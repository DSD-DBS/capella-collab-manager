# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add CDO port to T4C Instance.

Revision ID: fdff657f3cc1
Revises: 8eceebe9b3ea
Create Date: 2022-11-03 10:19:48.397946

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fdff657f3cc1"
down_revision = "9a1e6729858b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "t4c_instances",
        sa.Column(
            "cdo_port", sa.Integer(), nullable=False, server_default="12036"
        ),
    )
    op.create_check_constraint(
        "t4c_instances_cdo_port_check",
        "t4c_instances",
        "(cdo_port >= 0) AND (cdo_port <= 65535)",
    )
