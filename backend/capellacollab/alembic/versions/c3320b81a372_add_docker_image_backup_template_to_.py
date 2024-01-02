# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add docker_image_backup_template to tools

Revision ID: c3320b81a372
Revises: 4f273887f742
Create Date: 2022-11-09 15:00:59.177753

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c3320b81a372"
down_revision = "4f273887f742"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tools",
        sa.Column("docker_image_backup_template", sa.String(), nullable=True),
    )
