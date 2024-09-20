# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add repository id to git model and remove unused git model name

Revision ID: abddaf015966
Revises: 028c72ddfd20
Create Date: 2024-08-12 11:43:34.158404

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "abddaf015966"
down_revision = "028c72ddfd20"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "git_models", sa.Column("repository_id", sa.String(), nullable=True)
    )
    op.drop_column("git_models", "name")
