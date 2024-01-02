# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add model restrictions table

Revision ID: 4df9c82766e2
Revises: ca2346be296b
Create Date: 2022-12-21 12:01:00.653463

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4df9c82766e2"
down_revision = "ca2346be296b"
branch_labels = None
depends_on = None


def upgrade():
    t_model_restrictions = op.create_table(
        "model_restrictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=True),
        sa.Column(
            "allow_pure_variants",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.ForeignKeyConstraint(
            ["model_id"],
            ["models.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_model_restrictions_id"),
        "model_restrictions",
        ["id"],
        unique=True,
    )

    t_models = sa.Table(
        "models",
        sa.MetaData(),
        sa.Column("id", sa.Integer()),
    )

    connection = op.get_bind()
    models = connection.execute(
        sa.select(
            t_models.c.id,
        )
    )

    op.bulk_insert(
        t_model_restrictions,
        [{"model_id": model_id[0]} for model_id in models],
    )
