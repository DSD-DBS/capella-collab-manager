# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Replace project name with id for ProjectUserAssociation foreign key.

Revision ID: 16398dfaeef7
Revises: 7617cde6fbb1
Create Date: 2022-11-25 13:02:19.197569

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "16398dfaeef7"
down_revision = "7617cde6fbb1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_user_association",
        sa.Column("project_id", sa.Integer(), nullable=True),
    )
    op.drop_constraint(
        "project_user_association_projects_name_fkey",
        "project_user_association",
        type_="foreignkey",
    )
    op.get_bind().execute(
        sa.text(
            "UPDATE project_user_association SET project_id = id FROM projects WHERE project_user_association.projects_name = projects.name;"
        )
    )
    op.alter_column("project_user_association", "project_id", nullable=False)
    op.create_foreign_key(
        None, "project_user_association", "projects", ["project_id"], ["id"]
    )
    op.drop_column("project_user_association", "projects_name")
