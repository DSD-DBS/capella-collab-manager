# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


"""Add config dockerimages table

Revision ID: 703517ca79bc
Revises: 951433f1f092
Create Date: 2022-05-27 12:27:22.682178

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "703517ca79bc"
down_revision = "951433f1f092"
branch_labels = None
depends_on = None


def upgrade():
    table = op.create_table(
        "config_dockerimages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("environment", sa.String(), nullable=True),
        sa.Column("persistentworkspace", sa.String(), nullable=True),
        sa.Column("readonlyworkspace", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_config_dockerimages_id"),
        "config_dockerimages",
        ["id"],
        unique=False,
    )

    op.bulk_insert(
        table,
        [
            {
                "environment": "default",
                "persistentworkspace": "/capella/remote",
                "readonlyworkspace": "/capella/readonly",
            }
        ],
    )
