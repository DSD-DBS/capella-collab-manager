# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add t4c_repositories table


Revision ID: 5a6b36abdf25
Revises: cf93aadf77d6
Create Date: 2022-10-06 15:06:40.370022

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5a6b36abdf25"
down_revision = "3fa75ddfdde8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "t4c_repositories",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "instance_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["instance_id"],
            ["t4c_instances.id"],
            name="t4c_repositories_instance_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="t4c_repositories_pkey"),
    )
    op.create_unique_constraint(
        None, "t4c_repositories", ["instance_id", "name"]
    )
    op.create_index(
        "ix_t4c_repositories_id", "t4c_repositories", ["id"], unique=True
    )
