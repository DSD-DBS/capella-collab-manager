# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add DatabaseProject

Revision ID: 6a8bdec1dccb
Revises: c926d3e402a8
Create Date: 2021-09-02 16:10:04.355412

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6a8bdec1dccb"
down_revision = "c926d3e402a8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("repository_name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["repository_name"],
            ["repositories.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)
    op.create_index(
        op.f("ix_projects_name"), "projects", ["name"], unique=True
    )
