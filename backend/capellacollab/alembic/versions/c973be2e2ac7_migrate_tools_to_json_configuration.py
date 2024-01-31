# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Migrate tools to JSON configuration

Revision ID: c973be2e2ac7
Revises: 86ab7d4d1684
Create Date: 2024-01-31 17:40:31.743565

"""
import typing as t

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c973be2e2ac7"
down_revision = "86ab7d4d1684"
branch_labels = None
depends_on = None

t_tools = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("docker_image_backup_template", sa.String()),
    sa.Column("docker_image_template", sa.String()),
    sa.Column("readonly_docker_image_template", sa.String()),
)

t_tools_new = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text())),
)

t_integration = sa.Table(
    "tool_integrations",
    sa.MetaData(),
    sa.Column("t4c", sa.Boolean()),
    sa.Column("pure_variants", sa.Boolean()),
    sa.Column("jupyter", sa.Boolean()),
    sa.Column("tool_id", sa.Integer()),
)

t_tool_versions = sa.Table(
    "versions",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("is_deprecated", sa.Boolean()),
    sa.Column("is_recommended", sa.Boolean()),
    sa.Column("tool_id", sa.Integer()),
)

t_tool_versions_new = sa.Table(
    "versions",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("config", postgresql.JSONB(astext_type=sa.Text())),
)


def upgrade():
    connection = op.get_bind()
    tools = connection.execute(sa.select(t_tools)).mappings().all()

    tool_version_mapping = get_mapping_version_id_to_config(tools)
    tool_mapping = get_mapping_tool_id_to_integrations(tools)

    drop_table_and_columns()

    for tool_version_id, config in tool_version_mapping.items():
        connection.execute(
            sa.update(t_tool_versions_new)
            .where(t_tool_versions_new.c.id == tool_version_id)
            .values(config=config)
        )

    for tool_id, integrations in tool_mapping.items():
        connection.execute(
            sa.update(t_tools_new)
            .where(t_tools_new.c.id == tool_id)
            .values(integrations=integrations)
        )


def drop_table_and_columns():
    op.drop_table("tool_integrations")
    op.add_column(
        "tools",
        sa.Column(
            "integrations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    op.drop_column("tools", "docker_image_backup_template")
    op.drop_column("tools", "docker_image_template")
    op.drop_column("tools", "readonly_docker_image_template")
    op.add_column(
        "versions",
        sa.Column(
            "config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.drop_column("versions", "is_deprecated")
    op.drop_column("versions", "is_recommended")


def get_mapping_version_id_to_config(tools: t.Sequence[sa.RowMapping]):
    connection = op.get_bind()
    mapping = {}
    for tool in tools:
        versions = (
            connection.execute(
                sa.select(t_tool_versions).where(
                    tool["id"] == t_tool_versions.c.tool_id
                )
            )
            .mappings()
            .all()
        )

        for version in versions:
            mapping[version["id"]] = {
                "is_recommended": version["is_recommended"],
                "is_deprecated": version["is_deprecated"],
                "sessions": {
                    "persistent": {
                        "image": replace_dollar_with_format_syntax(
                            tool["docker_image_template"]
                        ),
                    },
                    "read_only": {
                        "image": replace_dollar_with_format_syntax(
                            tool["readonly_docker_image_template"]
                        ),
                    },
                },
                "backups": {
                    "image": replace_dollar_with_format_syntax(
                        tool["docker_image_backup_template"]
                    ),
                },
            }

    return mapping


def get_mapping_tool_id_to_integrations(tools: t.Sequence[sa.RowMapping]):
    connection = op.get_bind()
    mapping = {}
    for tool in tools:
        integration = (
            connection.execute(
                sa.select(t_integration).where(
                    t_integration.c.tool_id == tool["id"]
                )
            )
            .mappings()
            .first()
        )

        if not integration:
            continue

        mapping[tool["id"]] = {
            "t4c": integration["t4c"],
            "pure_variants": integration["pure_variants"],
            "jupyter": integration["jupyter"],
        }

    return mapping


def replace_dollar_with_format_syntax(template: str | None):
    return template.replace("$version", "{version}") if template else None
