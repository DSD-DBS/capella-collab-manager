# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


"""Add slug to project

Revision ID: 59233c4fb19f
Revises: 703517ca79bc
Create Date: 2022-07-18 10:16:36.889349

"""

import sqlalchemy as sa
from alembic import op
from slugify import slugify

# revision identifiers, used by Alembic.
revision = "59233c4fb19f"
down_revision = "703517ca79bc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("projects", sa.Column("slug", sa.String(), nullable=True))
    op.create_index(
        op.f("ix_projects_slug"), "projects", ["slug"], unique=True
    )
    t_projects = sa.Table(
        "projects",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
        sa.Column("name", sa.String()),
        sa.Column("slug", sa.String()),
    )
    connection = op.get_bind()
    projects = connection.execute(
        sa.select(
            t_projects.c.id,
            t_projects.c.name,
        )
    )

    # Names were not unique before, therefore conflicts can occur.
    # If there is a conflicts with slugs, they get a suffix with a counting number.
    existing_slugs = []
    for id_, name in projects:
        base_slug = slugify(name)
        slug = base_slug
        index = 0
        while slug in existing_slugs:
            slug = f"{base_slug}-{index}"
            index += 1
        existing_slugs.append(slug)
        connection.execute(
            t_projects.update()
            .where(t_projects.c.id == id_)
            .values(
                slug=slug,
            )
        )
    op.alter_column("projects", "slug", nullable=False)
