# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


"""Rename tables

Revision ID: 19a2ff65e57a
Revises: 0a16fb85f762
Create Date: 2022-05-09 14:30:00.602652

"""

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
