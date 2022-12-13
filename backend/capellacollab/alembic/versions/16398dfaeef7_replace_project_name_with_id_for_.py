# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
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
        "UPDATE project_user_association SET project_id = id FROM projects WHERE project_user_association.projects_name = projects.name;"
    )
    op.alter_column("project_user_association", "project_id", nullable=False)
    op.create_foreign_key(
        None, "project_user_association", "projects", ["project_id"], ["id"]
    )
    op.drop_column("project_user_association", "projects_name")


def downgrade():
    op.add_column(
        "project_user_association",
        sa.Column(
            "projects_name", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        "project_user_association_project_id_fkey",
        "project_user_association",
        type_="foreignkey",
    )
    op.get_bind().execute(
        "UPDATE project_user_association SET projects_name = name FROM projects WHERE project_user_association.project_id = projects.id;"
    )
    op.alter_column(
        "project_user_association", "projects_name", nullable=False
    )
    op.create_foreign_key(
        "project_user_association_projects_name_fkey",
        "project_user_association",
        "projects",
        ["projects_name"],
        ["name"],
    )
    op.drop_column("project_user_association", "project_id")
