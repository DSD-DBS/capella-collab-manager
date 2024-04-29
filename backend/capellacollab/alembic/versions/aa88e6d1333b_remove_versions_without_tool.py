# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove versions without tool

Revision ID: aa88e6d1333b
Revises: e06d616469ec
Create Date: 2024-04-25 10:48:56.205850

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "aa88e6d1333b"
down_revision = "e06d616469ec"
branch_labels = None
depends_on = None

t_versions = sa.Table(
    "versions",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("tool_id", sa.Integer()),
)

t_natures = sa.Table(
    "types",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("tool_id", sa.Integer()),
)


def upgrade():
    connection = op.get_bind()
    connection.execute(
        sa.delete(t_versions).where(t_versions.c.tool_id.is_(None))
    )
    connection.execute(
        sa.delete(t_natures).where(t_natures.c.tool_id.is_(None))
    )
    op.alter_column(
        "types", "tool_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "versions", "tool_id", existing_type=sa.INTEGER(), nullable=False
    )
