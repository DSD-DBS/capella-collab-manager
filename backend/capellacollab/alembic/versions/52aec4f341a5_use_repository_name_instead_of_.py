# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Use repository_name instead of repository_id as Foreign Key

Revision ID: 52aec4f341a5
Revises: bfafdd03e30c
Create Date: 2021-08-24 18:23:41.922890

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "52aec4f341a5"
down_revision = "bfafdd03e30c"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "git_models", sa.Column("repository_name", sa.String(), nullable=False)
    )
    op.drop_constraint(
        "git_models_repository_id_fkey", "git_models", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "git_models", "repositories", ["repository_name"], ["name"]
    )
    op.drop_column("git_models", "repository_id")
