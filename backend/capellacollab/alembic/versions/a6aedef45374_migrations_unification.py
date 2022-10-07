# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Migrations unification

Revision ID: a6aedef45374
Revises: d64fc5a97252
Create Date: 2022-10-04 21:33:16.207138

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a6aedef45374"
down_revision = "d64fc5a97252"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "models", "slug", existing_type=sa.VARCHAR(), nullable=False
    )
    op.create_index(op.f("ix_models_id"), "models", ["id"], unique=True)
    op.create_index(op.f("ix_models_name"), "models", ["name"], unique=False)
    op.alter_column(
        "projects", "slug", existing_type=sa.VARCHAR(), nullable=False
    )


def downgrade():
    op.alter_column(
        "projects", "slug", existing_type=sa.VARCHAR(), nullable=True
    )
    op.drop_index(op.f("ix_models_name"), table_name="models")
    op.drop_index(op.f("ix_models_id"), table_name="models")
    op.alter_column(
        "models", "slug", existing_type=sa.VARCHAR(), nullable=True
    )
