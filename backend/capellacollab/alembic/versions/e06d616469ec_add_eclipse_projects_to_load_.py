# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add `ECLIPSE_PROJECTS_TO_LOAD` environment variable

Revision ID: e06d616469ec
Revises: 7683b08b00ba
Create Date: 2024-04-16 15:32:33.123817

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "e06d616469ec"
down_revision = "7683b08b00ba"
branch_labels = None
depends_on = None


t_tools = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text())),
    sa.Column("config", postgresql.JSONB(astext_type=sa.Text())),
)


def upgrade():
    connection = op.get_bind()
    tools = connection.execute(sa.select(t_tools)).mappings().all()

    for tool in tools:
        if not tool["integrations"]["jupyter"]:
            tool["config"]["environment"] = tool["config"]["environment"] | {
                "ECLIPSE_PROJECTS_TO_LOAD": "{CAPELLACOLLAB_SESSION_PROVISIONING}",
            }

        connection.execute(
            sa.update(t_tools)
            .where(t_tools.c.id == tool["id"])
            .values(config=tool["config"])
        )
