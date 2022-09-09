# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


"""Rename tables

Revision ID: 19a2ff65e57a
Revises: 0a16fb85f762
Create Date: 2022-05-09 14:30:00.602652

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "19a2ff65e57a"
down_revision = "0a16fb85f762"
branch_labels = None
depends_on = None


# I cannot recommend renaming database tables
# unless you have a lot of fun writing migration scripts
def upgrade():

    # Rename the tables
    op.rename_table("projects", "t4c_models")
    op.rename_table("repositories", "projects")
    op.rename_table("repository_user_association", "project_user_association")

    # Update references in git_models
    op.alter_column(
        "git_models", "repository_name", new_column_name="project_name"
    )
    op.drop_constraint(
        "git_models_repository_name_fkey", "git_models", type_="foreignkey"
    )

    # Update references in EASEBackup
    op.drop_constraint(
        "EASEBackup_project_fkey", "EASEBackup", type_="foreignkey"
    )

    # Update references in project_user_association
    op.alter_column(
        "project_user_association",
        "repository_name",
        new_column_name="projects_name",
    )
    op.drop_constraint(
        "repository_user_association_repository_name_fkey",
        "project_user_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        "repository_user_association_username_fkey",
        "project_user_association",
        type_="foreignkey",
    )

    op.alter_column(
        "t4c_models", "repository_name", new_column_name="project_name"
    )
    op.drop_constraint(
        "projects_repository_name_fkey", "t4c_models", type_="foreignkey"
    )

    # Update index names for t4c_models
    op.drop_index("ix_projects_name", table_name="t4c_models")
    op.drop_index("ix_projects_id", table_name="t4c_models")
    op.create_index(
        op.f("ix_t4c_models_id"), "t4c_models", ["id"], unique=True
    )
    op.create_index(
        op.f("ix_t4c_models_name"), "t4c_models", ["name"], unique=False
    )

    # Update index names for projects
    op.drop_index("ix_repositories_id", table_name="projects")
    op.drop_index("ix_repositories_name", table_name="projects")
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=True)
    op.create_index(
        op.f("ix_projects_name"), "projects", ["name"], unique=True
    )

    # Create foreign keys again
    op.create_foreign_key(
        None,
        "git_models",
        "projects",
        ["project_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "project_user_association",
        "projects",
        ["projects_name"],
        ["name"],
    )
    op.create_foreign_key(
        None, "project_user_association", "users", ["username"], ["name"]
    )
    op.create_foreign_key(
        None,
        "t4c_models",
        "projects",
        ["project_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None, "EASEBackup", "projects", ["project"], ["name"]
    )


def downgrade():
    op.rename_table("projects", "repositories")
    op.rename_table("t4c_models", "projects")
    op.rename_table("project_user_association", "repository_user_association")

    op.alter_column(
        "git_models", "project_name", new_column_name="repository_name"
    )
    op.drop_constraint(
        "git_models_project_name_fkey", "git_models", type_="foreignkey"
    )

    op.drop_constraint(
        "EASEBackup_project_fkey", "EASEBackup", type_="foreignkey"
    )

    op.alter_column(
        "repository_user_association",
        "projects_name",
        new_column_name="repository_name",
    )
    op.drop_constraint(
        "project_user_association_projects_name_fkey",
        "repository_user_association",
        type_="foreignkey",
    )
    op.drop_constraint(
        "project_user_association_username_fkey",
        "repository_user_association",
        type_="foreignkey",
    )

    op.alter_column(
        "projects", "project_name", new_column_name="repository_name"
    )
    op.drop_constraint(
        "t4c_models_project_name_fkey", "projects", type_="foreignkey"
    )

    # Update index names for projects
    op.drop_index(op.f("ix_projects_name"), table_name="repositories")
    op.drop_index(op.f("ix_projects_id"), table_name="repositories")
    op.create_index(
        "ix_repositories_name", "repositories", ["name"], unique=True
    )
    op.create_index("ix_repositories_id", "repositories", ["id"], unique=True)

    # Update index names for t4c_models
    op.drop_index("ix_t4c_models_id", table_name="projects")
    op.drop_index("ix_t4c_models_name", table_name="projects")
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=True)
    op.create_index(
        op.f("ix_projects_name"), "projects", ["name"], unique=False
    )

    op.create_foreign_key(
        None,
        "git_models",
        "repositories",
        ["repository_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "repository_user_association",
        "repositories",
        ["repository_name"],
        ["name"],
    )
    op.create_foreign_key(
        None,
        "repository_user_association",
        "users",
        ["username"],
        ["name"],
    )
    op.create_foreign_key(
        None,
        "projects",
        "repositories",
        ["repository_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None, "EASEBackup", "repositories", ["project"], ["name"]
    )
