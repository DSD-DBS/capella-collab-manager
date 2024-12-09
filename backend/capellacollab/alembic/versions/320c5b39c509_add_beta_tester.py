# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add Beta Tester

Revision ID: 320c5b39c509
Revises: 3818a5009130
Create Date: 2024-11-04 12:31:17.024627

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "320c5b39c509"
down_revision = "3818a5009130"
branch_labels = None
depends_on = None


t_tool_versions = sa.Table(
    "versions",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("config", postgresql.JSONB(astext_type=sa.Text())),
)


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "beta_tester", sa.Boolean(), nullable=False, server_default="false"
        ),
    )

    op.add_column(
        "feedback",
        sa.Column(
            "beta_tester", sa.Boolean(), nullable=False, server_default="false"
        ),
    )

    connection = op.get_bind()
    results = connection.execute(sa.select(t_tool_versions)).mappings().all()

    for row in results:
        config = row["config"]
        config["sessions"]["persistent"]["image"] = {
            "regular": config["sessions"]["persistent"]["image"],
            "beta": None,
        }

        connection.execute(
            sa.update(t_tool_versions)
            .where(t_tool_versions.c.id == row["id"])
            .values(config=config)
        )
