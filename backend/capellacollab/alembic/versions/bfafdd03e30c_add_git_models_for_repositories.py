# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add Git models for repositories

Revision ID: bfafdd03e30c
Revises: f3efdcedfdde
Create Date: 2021-08-24 12:54:08.768420

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bfafdd03e30c"
down_revision = "f3efdcedfdde"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "git_models",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("entrypoint", sa.String(), nullable=True),
        sa.Column("revision", sa.String(), nullable=True),
        sa.Column("primary", sa.Boolean(), nullable=True),
        sa.Column("repository_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["repository_id"],
            ["repositories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_git_models_id"), "git_models", ["id"], unique=False
    )
