# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add backups table

Revision ID: fcf5d69d7bbc
Revises: e7a140389e22
Create Date: 2022-11-07 13:33:24.231968

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fcf5d69d7bbc"
down_revision = "fdff657f3cc1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "backups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("k8s_cronjob_id", sa.String(), nullable=True),
        sa.Column("git_model_id", sa.Integer(), nullable=True),
        sa.Column("t4c_model_id", sa.Integer(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=True),
        sa.Column("model_id", sa.Integer(), nullable=True),
        sa.Column("t4c_username", sa.String(), nullable=True),
        sa.Column("t4c_password", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["git_model_id"],
            ["git_models.id"],
        ),
        sa.ForeignKeyConstraint(
            ["model_id"],
            ["models.id"],
        ),
        sa.ForeignKeyConstraint(
            ["t4c_model_id"],
            ["t4c_models.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_backups_id"), "backups", ["id"], unique=False)
    op.drop_index("ix_EASEBackup_id", table_name="EASEBackup")
    op.drop_table("EASEBackup")
