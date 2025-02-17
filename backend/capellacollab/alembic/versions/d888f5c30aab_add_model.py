# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


"""Add model

Revision ID: d888f5c30aab
Revises: 59233c4fb19f
Create Date: 2022-08-08 11:45:54.628905

"""

import sqlalchemy as sa
from alembic import op
from slugify import slugify

# revision identifiers, used by Alembic.
revision = "d888f5c30aab"
down_revision = "59233c4fb19f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tools",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("docker_image_template", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("tool_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tools.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tool_id", "name"),
    )
    op.create_table(
        "versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("is_recommended", sa.Boolean(), nullable=True),
        sa.Column("is_deprecated", sa.Boolean(), nullable=True),
        sa.Column("tool_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tool_id"],
            ["tools.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tool_id", "name"),
    )
    op.rename_table("capella_models", "models")

    with op.batch_alter_table("models") as batch_op:
        batch_op.add_column(sa.Column("slug", sa.String(), nullable=True))
        batch_op.add_column(
            sa.Column("project_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(sa.Column("tool_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("version_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(sa.Column("type_id", sa.Integer(), nullable=True))

    t_models = sa.Table(
        "models",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
        sa.Column("name", sa.String()),
        sa.Column("slug", sa.String()),
        sa.Column("project_name", sa.String()),
        sa.Column("project_id", sa.Integer()),
    )
    t_projects = sa.Table(
        "projects",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
        sa.Column("name", sa.String()),
    )

    with op.batch_alter_table("models") as batch_op:
        joined = t_models.join(
            t_projects, t_models.c.project_name == t_projects.c.name
        )
        connection = op.get_bind()
        models = connection.execute(
            sa.select(
                t_models.c.id,
                t_models.c.name,
                t_projects.c.id,
            ).select_from(joined)
        )

        # Names were not unique before, therefore conflicts can occur.
        # Model slugs have to unique per project.
        # If there is a conflicts with slugs, they get a suffix with a counting number.
        existing_slugs = {}
        for id_, name, project_id in models:
            if project_id not in existing_slugs:
                existing_slugs[project_id] = []

            base_slug = slugify(name)
            slug = base_slug
            index = 0

            while slug in existing_slugs[project_id]:
                slug = f"{base_slug}-{index}"
                index += 1

            existing_slugs[project_id].append(slug)
            connection.execute(
                t_models.update()
                .where(t_models.c.id == id_)
                .values(
                    slug=slug,
                    project_id=project_id,
                )
            )

        batch_op.alter_column("slug", nullable=False)
        batch_op.create_foreign_key(None, "projects", ["project_id"], ["id"])

        batch_op.create_unique_constraint(None, ["project_id", "slug"])
        batch_op.drop_constraint(
            "capella_models_project_name_fkey", "foreignkey"
        )
        batch_op.create_foreign_key(None, "projects", ["project_id"], ["id"])
        batch_op.create_foreign_key(None, "versions", ["version_id"], ["id"])
        batch_op.create_foreign_key(None, "tools", ["tool_id"], ["id"])
        batch_op.create_foreign_key(None, "types", ["type_id"], ["id"])

        batch_op.drop_column("project_name")
