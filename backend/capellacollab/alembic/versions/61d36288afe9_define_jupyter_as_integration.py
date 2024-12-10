# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Define Jupyter as integration

Revision ID: 61d36288afe9
Revises: f3d2dedd7906
Create Date: 2023-02-09 11:57:07.345877

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "61d36288afe9"
down_revision = "f3d2dedd7906"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tool_integrations",
        sa.Column(
            "jupyter", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
