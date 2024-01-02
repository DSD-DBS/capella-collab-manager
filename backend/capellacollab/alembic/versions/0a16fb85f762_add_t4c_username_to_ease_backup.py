# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add t4c username to ease backup

Revision ID: 0a16fb85f762
Revises: d6a23ac7f263
Create Date: 2022-03-04 14:00:41.976888

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0a16fb85f762"
down_revision = "d6a23ac7f263"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "EASEBackup", sa.Column("username", sa.String(), nullable=True)
    )
