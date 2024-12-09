# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Make tool name required

Revision ID: 1a4208c18909
Revises: d8cf851562cd
Create Date: 2023-09-19 11:25:16.343948

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1a4208c18909"
down_revision = "d8cf851562cd"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "tools",
        "name",
        existing_type=sa.String(),
        nullable=False,
    )
