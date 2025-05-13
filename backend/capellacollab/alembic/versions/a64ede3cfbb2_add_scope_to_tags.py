# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add scope to tags

Revision ID: a64ede3cfbb2
Revises: 40b857af236a
Create Date: 2025-05-13 12:45:21.293441

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a64ede3cfbb2"
down_revision = "40b857af236a"
branch_labels = None
depends_on = None


def upgrade():
    sa.Enum("PROJECT", "USER", name="tagscope").create(op.get_bind())
    op.add_column(
        "tags",
        sa.Column(
            "scope",
            postgresql.ENUM(
                "PROJECT", "USER", name="tagscope", create_type=False
            ),
            nullable=False,
            server_default="PROJECT",
        ),
    )
