# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""update DatabaseT4CModel table

Revision ID: e7a140389e22
Revises: 5a6b36abdf25
Create Date: 2022-10-12 14:43:58.270916

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e7a140389e22"
down_revision = "5a6b36abdf25"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "t4c_models", sa.Column("repository_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "t4c_models", "t4c_repositories", ["repository_id"], ["id"]
    )
    op.alter_column(
        "t4c_repositories",
        "instance_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )
    op.create_unique_constraint(None, "t4c_models", ["repository_id", "name"])


def downgrade():
    op.drop_constraint(
        "t4c_models_repository_id_name_key", "t4c_models", type_="unique"
    )
    op.alter_column(
        "t4c_repositories",
        "instance_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
    op.drop_constraint(
        op.f("t4c_models_repository_id_fkey"), "t4c_models", type_="foreignkey"
    )
    op.drop_column("t4c_models", "repository_id")
