# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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
down_revision = "e7a140389e22"
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
    op.drop_constraint(
        "t4c_instances_name_key", "t4c_instances", type_="unique"
    )
    op.create_unique_constraint(None, "types", ["tool_id", "name"])
    op.create_unique_constraint(None, "versions", ["tool_id", "name"])


def downgrade():
    op.drop_constraint(None, "versions", type_="unique")
    op.drop_constraint(None, "types", type_="unique")
    op.create_unique_constraint(
        "t4c_instances_name_key", "t4c_instances", ["name"]
    )
    op.create_table(
        "EASEBackup",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text(
                "nextval('\"EASEBackup_id_seq\"'::regclass)"
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "gitmodel", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "t4cmodel", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "project", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "reference", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "username", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["gitmodel"], ["git_models.id"], name="EASEBackup_gitmodel_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["project"], ["projects.name"], name="EASEBackup_project_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["t4cmodel"], ["t4c_models.id"], name="EASEBackup_t4cmodel_fkey"
        ),
        sa.PrimaryKeyConstraint("id", "project", name="EASEBackup_pkey"),
    )
    op.create_index("ix_EASEBackup_id", "EASEBackup", ["id"], unique=False)
    op.drop_index(op.f("ix_backups_id"), table_name="backups")
    op.drop_table("backups")
