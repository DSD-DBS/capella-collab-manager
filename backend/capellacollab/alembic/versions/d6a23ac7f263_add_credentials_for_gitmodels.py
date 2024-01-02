# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add credentials for gitmodels

Revision ID: d6a23ac7f263
Revises: caa0ecb7b28d
Create Date: 2022-03-04 11:47:41.439896

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d6a23ac7f263"
down_revision = "caa0ecb7b28d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "EASEBackup", sa.Column("reference", sa.String(), nullable=True)
    )
    op.add_column(
        "git_models",
        sa.Column("username", sa.String(), nullable=True, server_default=""),
    )
    op.add_column(
        "git_models", sa.Column("password", sa.String(), nullable=True)
    )
    op.drop_constraint(
        "git_models_project_id_fkey", "git_models", type_="foreignkey"
    )
    op.drop_column("git_models", "project_id")
