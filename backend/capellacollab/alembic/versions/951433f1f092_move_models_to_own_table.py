# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


"""Move models to own table

Revision ID: 951433f1f092
Revises: c8e50c0daee1
Create Date: 2022-05-16 12:49:07.592601

"""


import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "951433f1f092"
down_revision = "c8e50c0daee1"
branch_labels = None
depends_on = None


def upgrade():
    # Create new capella_models table
    op.create_table(
        "capella_models",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column(
            "description", sa.String(), nullable=True, server_default=""
        ),
        sa.Column(
            "editing_mode",
            sa.Enum("T4C", "GIT", name="editingmode"),
            nullable=True,
        ),
        sa.Column(
            "model_type",
            sa.Enum("PROJECT", "LIBRARY", name="capellamodeltype"),
            nullable=True,
        ),
        sa.Column("project_name", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_name"],
            ["projects.name"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_capella_models_id"), "capella_models", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_capella_models_name"),
        "capella_models",
        ["name"],
        unique=False,
    )

    # Fetch all models
    conn = op.get_bind()
    git_models = conn.execute("SELECT * FROM git_models")
    t4c_models = conn.execute("SELECT * FROM t4c_models")

    # Update foreign keys
    op.add_column(
        "git_models", sa.Column("model_id", sa.Integer(), nullable=True)
    )
    op.drop_constraint(
        "git_models_project_name_fkey", "git_models", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "git_models", "capella_models", ["model_id"], ["id"]
    )
    op.drop_column("git_models", "project_name")

    op.add_column(
        "t4c_models", sa.Column("model_id", sa.Integer(), nullable=True)
    )
    op.drop_constraint(
        "t4c_models_project_name_fkey", "t4c_models", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "t4c_models", "capella_models", ["model_id"], ["id"]
    )
    op.drop_column("t4c_models", "project_name")

    # Update values of foreign keys
    for model in git_models:
        id = model.id
        name = model.name
        project_name = model.project_name
        model_id = conn.execute(
            f"INSERT INTO capella_models (name, editing_mode, model_type, project_name) VALUES ('{name}', 'GIT', 'PROJECT', '{project_name}') RETURNING *;"
        ).fetchone()[0]

        op.execute(f"UPDATE git_models SET model_id={model_id} WHERE id={id}")

    for model in t4c_models:
        id = model.id
        name = model.name
        project_name = model.project_name
        model_id = conn.execute(
            f"INSERT INTO capella_models (name, editing_mode, model_type, project_name) VALUES ('{name}', 'T4C', 'PROJECT', '{project_name}') RETURNING *;"
        ).fetchone()[0]

        op.execute(f"UPDATE t4c_models SET model_id={model_id} WHERE id={id}")


def downgrade():
    conn = op.get_bind()
    models = conn.execute("SELECT * FROM capella_models").fetchall()
    git_models = conn.execute("SELECT * FROM git_models").fetchall()
    t4c_models = conn.execute("SELECT * FROM t4c_models").fetchall()

    op.add_column(
        "t4c_models",
        sa.Column(
            "project_name", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        "t4c_models_model_id_fkey", "t4c_models", type_="foreignkey"
    )
    op.create_foreign_key(
        "t4c_models_project_name_fkey",
        "t4c_models",
        "projects",
        ["project_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.drop_column("t4c_models", "model_id")
    op.add_column(
        "git_models",
        sa.Column(
            "project_name", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
    )
    op.drop_constraint(
        "git_models_model_id_fkey", "git_models", type_="foreignkey"
    )
    op.create_foreign_key(
        "git_models_project_name_fkey",
        "git_models",
        "projects",
        ["project_name"],
        ["name"],
        ondelete="CASCADE",
    )
    op.drop_column("git_models", "model_id")
    op.drop_index(op.f("ix_capella_models_name"), table_name="capella_models")
    op.drop_index(op.f("ix_capella_models_id"), table_name="capella_models")
    op.drop_table("capella_models")

    editing_mode = postgresql.ENUM("T4C", "GIT", name="editingmode")
    editing_mode.drop(op.get_bind())

    model_type = postgresql.ENUM("PROJECT", "LIBRARY", name="capellamodeltype")
    model_type.drop(op.get_bind())

    for git_model in git_models:
        id = git_model.id
        project_name = next(
            (
                model.project_name
                for model in models
                if model.id == git_model.model_id
            )
        )
        op.execute(
            f"UPDATE git_models SET project_name='{project_name}' WHERE id={id}"
        )

    for t4c_model in t4c_models:
        id = t4c_model.id
        project_name = next(
            (
                model.project_name
                for model in models
                if model[0] == t4c_model[-1]
            )
        )
        op.execute(
            f"UPDATE t4c_models SET project_name='{project_name}' WHERE id={id}"
        )

    op.alter_column("git_models", "project_name", nullable=False)
    op.alter_column("t4c_models", "project_name", nullable=False)
