# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add resources to tools

Revision ID: 6c4ff61acc8e
Revises: 3ec39e345cc9
Create Date: 2024-02-15 14:21:18.085411

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6c4ff61acc8e"
down_revision = "3ec39e345cc9"
branch_labels = None
depends_on = None


t_tools = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text())),
)

t_tools_new = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("resources", postgresql.JSONB(astext_type=sa.Text())),
)


def upgrade():
    op.add_column(
        "tools",
        sa.Column(
            "resources",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    connection = op.get_bind()
    tools = connection.execute(sa.select(t_tools)).mappings().all()

    for tool in tools:
        if tool["integrations"]["jupyter"]:
            resources = {
                "cpu": {"requests": 1, "limits": 2},
                "memory": {"requests": "500Mi", "limits": "3Gi"},
            }
        else:
            resources = {
                "cpu": {"requests": 0.4, "limits": 2},
                "memory": {"requests": "1.6Gi", "limits": "6Gi"},
            }

        connection.execute(
            sa.update(t_tools_new)
            .where(t_tools_new.c.id == tool["id"])
            .values(resources=resources)
        )
