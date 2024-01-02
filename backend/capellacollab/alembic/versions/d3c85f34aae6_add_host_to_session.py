# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add host to Session

Revision ID: d3c85f34aae6
Revises: 2eeda6a7bd66
Create Date: 2021-08-24 08:15:01.443971

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d3c85f34aae6"
down_revision = "2eeda6a7bd66"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("sessions", sa.Column("host", sa.String(), nullable=True))
