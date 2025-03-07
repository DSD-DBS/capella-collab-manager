# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add general file-shares

Revision ID: b2fd698ed6cb
Revises: db35c7cfb407
Create Date: 2025-02-21 15:41:21.391386

"""

import datetime
import logging

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

logger = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = "b2fd698ed6cb"
down_revision = "db35c7cfb407"
branch_labels = None
depends_on = None

t_tool_models = sa.Table(
    "models",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("project_id", sa.Integer()),
    sa.Column("tool_id"),
    sa.Column("configuration", postgresql.JSONB(astext_type=sa.Text())),
)

t_tools = sa.Table(
    "tools",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("integrations", postgresql.JSONB(astext_type=sa.Text())),
)


def upgrade():
    t_project_volumes = op.create_table(
        "project_volumes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("pvc_name", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pvc_name"),
    )
    op.create_index(
        op.f("ix_project_volumes_id"), "project_volumes", ["id"], unique=False
    )

    connection = op.get_bind()
    tools = connection.execute(sa.select(t_tools)).mappings().all()

    jupyter_tool_ids = []
    for tool in tools:
        if tool["integrations"]["jupyter"]:
            jupyter_tool_ids.append(tool["id"])

        integrations = tool["integrations"]
        del integrations["jupyter"]
        connection.execute(
            sa.update(t_tools)
            .where(t_tools.c.id == tool["id"])
            .values(integrations=integrations)
        )

    tool_models = (
        connection.execute(
            sa.select(t_tool_models).where(
                t_tool_models.c.tool_id.in_(jupyter_tool_ids)
            )
        )
        .mappings()
        .all()
    )

    grouped_by_project = {}
    for tool_model in tool_models:
        logger.info(
            "Adding general file share for Jupyter model %s in project %s",
            tool_model["id"],
            tool_model["project_id"],
        )

        project_id = tool_model["project_id"]
        if project_id in grouped_by_project:
            raise ValueError(
                "Due a removal of the abstraction layer for"
                " Jupyter file-shares, it's no longer possible to"
                " have multiple file-shares in one project."
                f" In the project {project_id} we've identified multiple Jupyter models."
                " Please rollback, merge the files in the file-shares manually"
                " and remove empty Jupyter models."
                " Then try again."
            )

        if "workspace" in tool_model["configuration"]:
            grouped_by_project[project_id] = {
                "created_at": datetime.datetime.now(tz=datetime.UTC),
                "pvc_name": "shared-workspace-"
                + tool_model["configuration"]["workspace"],
                "project_id": tool_model["project_id"],
                "size": "2Gi",
            }

    op.bulk_insert(
        t_project_volumes,
        list(grouped_by_project.values()),
    )
    op.drop_column("models", "configuration")
