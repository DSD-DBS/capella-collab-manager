# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add resource override

Revision ID: 4d42177579a2
Revises: 2f8449c217fa
Create Date: 2024-11-12 17:43:23.486104

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4d42177579a2"
down_revision = "2f8449c217fa"
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
    results = connection.execute(sa.select(t_tools)).mappings().all()

    for row in results:
        config = row["config"]
        config["resources"] = {
            "default_profile": {
                "cpu": config["resources"]["cpu"],
                "memory": config["resources"]["memory"],
            },
            "additional": {},
        }

        connection.execute(
            sa.update(t_tools)
            .where(t_tools.c.id == row["id"])
            .values(config=config)
        )
