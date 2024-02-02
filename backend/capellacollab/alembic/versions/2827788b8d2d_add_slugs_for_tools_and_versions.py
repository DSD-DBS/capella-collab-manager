# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Slugs for tools and versions

Revision ID: 2827788b8d2d
Revises: f55b41e32223
Create Date: 2023-11-07 11:15:07.753055

"""
import sqlalchemy as sa
from alembic import op
from slugify import slugify

revision = "2827788b8d2d"
down_revision = "f55b41e32223"
branch_labels = None
depends_on = None


def upgrade():
    for table_name in ("tools", "versions"):
        op.add_column(
            table_name,
            sa.Column("slug", sa.String(), unique=True, nullable=True),
        )

        connection = op.get_bind()
        rows = connection.execute(sa.text(f"SELECT * from {table_name}"))

        for row in rows:
            connection.execute(
                sa.text(
                    f"UPDATE {table_name} SET slug = '{slugify(row.name)}' WHERE id = {row.id};"
                )
            )

        op.alter_column(table_name, "slug", nullable=False)
