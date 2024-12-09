# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Project type

Revision ID: 5ca7037ef183
Revises: 0e2028f83156
Create Date: 2023-10-24 14:21:07.128985

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5ca7037ef183"
down_revision = "0e2028f83156"
branch_labels = None
depends_on = None


def upgrade():
    projecttype = sa.Enum("GENERAL", "TRAINING", name="projecttype")
    projecttype.create(op.get_bind())

    op.add_column(
        "projects",
        sa.Column(
            "type", projecttype, server_default="GENERAL", nullable=False
        ),
    )
