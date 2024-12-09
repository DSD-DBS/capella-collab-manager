# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Project visibility

Revision ID: 90abdec3827e
Revises: 3442c1b545e3
Create Date: 2023-07-10 09:24:26.635483

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "90abdec3827e"
down_revision = "3442c1b545e3"
branch_labels = None
depends_on = None


def upgrade():
    visibility = sa.Enum("PRIVATE", "INTERNAL", name="visibility")
    visibility.create(op.get_bind())

    op.add_column(
        "projects",
        sa.Column(
            "visibility",
            visibility,
            server_default="PRIVATE",
            nullable=False,
        ),
    )
