# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add JenkinsPipeline

Revision ID: f3ed32b2cfb0
Revises: fc6250459067
Create Date: 2021-09-06 16:24:02.228776

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f3ed32b2cfb0"
down_revision = "fc6250459067"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "jenkins",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("git_model_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["git_model_id"],
            ["git_models.id"],
        ),
        sa.PrimaryKeyConstraint("id", "git_model_id"),
    )
    op.create_index(op.f("ix_jenkins_id"), "jenkins", ["id"], unique=False)
