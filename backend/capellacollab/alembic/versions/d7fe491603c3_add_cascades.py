# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add cascades

Revision ID: d7fe491603c3
Revises: 7bdfe4e65e81
Create Date: 2021-09-08 10:38:53.633259

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d7fe491603c3"
down_revision = "9259062f0f62"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "git_models_repository_name_fkey", "git_models", type_="foreignkey"
    )
    op.drop_constraint(
        "git_models_project_id_fkey", "git_models", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "git_models",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "git_models",
        "repositories",
        ["repository_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "jenkins_git_model_id_fkey", "jenkins", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "jenkins",
        "git_models",
        ["git_model_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_constraint(
        "projects_repository_name_fkey", "projects", type_="foreignkey"
    )
    op.create_foreign_key(
        None,
        "projects",
        "repositories",
        ["repository_name"],
        ["name"],
        ondelete="CASCADE",
    )
