# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Use Project ID as reference instead of Project Name

Revision ID: fc6250459067
Revises: 377b60de4441
Create Date: 2021-09-03 15:29:23.047537

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "fc6250459067"
down_revision = "377b60de4441"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "git_models", sa.Column("project_id", sa.Integer(), nullable=False)
    )
    op.drop_constraint(
        "git_models_project_name_fkey", "git_models", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "git_models", "projects", ["project_id"], ["id"]
    )
    op.drop_column("git_models", "project_name")
