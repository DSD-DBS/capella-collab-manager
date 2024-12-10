# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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
    git_models = conn.execute(sa.text("SELECT * FROM git_models"))
    t4c_models = conn.execute(sa.text("SELECT * FROM t4c_models"))

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
        project_name = model.project_name

        model_id = get_or_create_model(conn, project_name)
        op.execute(
            sa.text(f"UPDATE git_models SET model_id={model_id} WHERE id={id}")
        )

    for model in t4c_models:
        id = model.id
        project_name = model.project_name
        model_id = get_or_create_model(conn, project_name)

        op.execute(
            sa.text(f"UPDATE t4c_models SET model_id={model_id} WHERE id={id}")
        )


def get_or_create_model(conn, project_name) -> int:
    models = conn.execute(
        sa.text(
            f"SELECT id FROM capella_models WHERE project_name='{project_name}';"
        )
    ).fetchone()

    if models:
        model_id = models[0]
    else:
        model_id = conn.execute(
            sa.text(
                f"INSERT INTO capella_models (name, editing_mode, model_type, project_name) VALUES ('{project_name}', 'GIT', 'PROJECT', '{project_name}') RETURNING *;"
            )
        ).fetchone()[0]

    return model_id
