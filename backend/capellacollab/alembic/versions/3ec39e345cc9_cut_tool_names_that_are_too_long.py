# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Cut tool names that are too long

Revision ID: 3ec39e345cc9
Revises: c973be2e2ac7
Create Date: 2024-02-23 08:53:31.142987

"""
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3ec39e345cc9"
down_revision = "c973be2e2ac7"
branch_labels = None
depends_on = None

t_tools = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("name", sa.String()),
)

t_tool_versions = sa.Table(
    "versions",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("name", sa.String()),
)

t_tool_natures = sa.Table(
    "types",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("name", sa.String()),
)


def upgrade():
    connection = op.get_bind()
    tools = connection.execute(sa.select(t_tools)).mappings().all()
    tools_versions = (
        connection.execute(sa.select(t_tool_versions)).mappings().all()
    )
    tools_natures = (
        connection.execute(sa.select(t_tool_natures)).mappings().all()
    )

    for tool in tools:
        if len(tool["name"]) < 30 and len(tool["name"]) > 1:
            continue

        name = update_tool_name(tool["name"])

        connection.execute(
            sa.update(t_tools)
            .where(t_tools.c.id == tool["id"])
            .values(name=name)
        )
    for version in tools_versions:
        if len(version["name"]) < 30 and len(version["name"]) > 1:
            continue

        name = update_tool_name(version["name"])

        connection.execute(
            sa.update(t_tool_versions)
            .where(t_tool_versions.c.id == version["id"])
            .values(name=name)
        )
    for nature in tools_natures:
        if len(nature["name"]) < 30 and len(nature["name"]) > 1:
            continue

        name = update_tool_name(nature["name"])

        connection.execute(
            sa.update(t_tool_natures)
            .where(t_tool_natures.c.id == nature["id"])
            .values(name=name)
        )


def update_tool_name(name: str) -> str:
    if len(name) < 2:
        return name + " (updated)"
    return name[:30]
