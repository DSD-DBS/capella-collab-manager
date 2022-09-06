# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add EASE backup table

Revision ID: caa0ecb7b28d
Revises: 687484695147
Create Date: 2022-03-03 14:20:15.424650

"""
# 3rd party:
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "caa0ecb7b28d"
down_revision = "687484695147"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "EASEBackup",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("gitmodel", sa.Integer(), nullable=True),
        sa.Column("t4cmodel", sa.Integer(), nullable=True),
        sa.Column("project", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["gitmodel"],
            ["git_models.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project"],
            ["repositories.name"],
        ),
        sa.ForeignKeyConstraint(
            ["t4cmodel"],
            ["projects.id"],
        ),
        sa.PrimaryKeyConstraint("id", "project"),
    )
    op.create_index(
        op.f("ix_EASEBackup_id"), "EASEBackup", ["id"], unique=False
    )


def downgrade():
    op.drop_index(op.f("ix_EASEBackup_id"), table_name="EASEBackup")
    op.drop_table("EASEBackup")
