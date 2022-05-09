# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add project attributes

Revision ID: c8e50c0daee1
Revises: 04482e6f1795
Create Date: 2022-05-09 15:07:16.515720

"""
# 3rd party:
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "c8e50c0daee1"
down_revision = "19a2ff65e57a"
branch_labels = None
depends_on = None


def upgrade():
    # Add description, editing_mode and project_type to project table

    op.add_column("projects", sa.Column("description", sa.String(), nullable=True))

    editingmode = postgresql.ENUM("T4C", "GIT", name="editingmode")
    editingmode.create(op.get_bind())
    op.add_column(
        "projects",
        sa.Column(
            "editing_mode", sa.Enum("T4C", "GIT", name="editingmode"), nullable=True
        ),
    )

    projecttype = postgresql.ENUM("PROJECT", "LIBRARY", name="projecttype")
    projecttype.create(op.get_bind())
    op.add_column(
        "projects",
        sa.Column(
            "project_type",
            sa.Enum("PROJECT", "LIBRARY", name="projecttype"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("projects", "project_type")

    op.drop_column("projects", "editing_mode")
    editingmode = postgresql.ENUM("T4C", "GIT", name="editingmode")
    editingmode.drop(op.get_bind())

    op.drop_column("projects", "description")
    projecttype = postgresql.ENUM("PROJECT", "LIBRARY", name="projecttype")
    projecttype.drop(op.get_bind())
