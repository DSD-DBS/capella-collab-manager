# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Set nullable to False for run_nightly and include_commit_history

Revision ID: 4f273887f742
Revises: df07aad6525d
Create Date: 2022-11-08 16:36:18.621808

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4f273887f742"
down_revision = "df07aad6525d"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "backups",
        "include_commit_history",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text("false"),
    )
    op.alter_column(
        "backups",
        "run_nightly",
        existing_type=sa.BOOLEAN(),
        nullable=False,
        existing_server_default=sa.text("true"),
    )
