# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add tool_integrations table

Revision ID: ca2346be296b
Revises: 0ef0826d54e7
Create Date: 2022-12-19 17:05:07.009764

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ca2346be296b"
down_revision = "0ef0826d54e7"
branch_labels = None
depends_on = None


def upgrade():
    t_tool_integrations = op.create_table(
        "tool_integrations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tool_id", sa.Integer(), nullable=True),
        sa.Column(
            "t4c", sa.Boolean(), nullable=True, server_default=sa.text("false")
        ),
        sa.Column(
            "pure_variants",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("false"),
        ),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tools.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    t_tools = sa.Table(
        "tools",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
    )

    connection = op.get_bind()
    tools = connection.execute(
        sa.select(
            t_tools.c.id,
        )
    )

    op.bulk_insert(
        t_tool_integrations, [{"tool_id": tool_id[0]} for tool_id in tools]
    )
