# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add workspaces table

Revision ID: a1e59021e0d0
Revises: 49f51db92903
Create Date: 2024-07-17 09:19:57.903328

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a1e59021e0d0"
down_revision = "49f51db92903"
branch_labels = None
depends_on = None

t_users = sa.Table(
    "users",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("name", sa.String()),
)


def upgrade():
    connection = op.get_bind()
    users = connection.execute(sa.select(t_users)).mappings().all()

    t_workspaces = op.create_table(
        "workspaces",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pvc_name", sa.String(), nullable=False),
        sa.Column("size", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id", "user_id"),
        sa.UniqueConstraint("pvc_name"),
    )
    op.create_index(
        op.f("ix_workspaces_id"), "workspaces", ["id"], unique=False
    )

    for user in users:
        pvc_name = (
            "persistent-session-"
            + user["name"].replace("@", "-at-").replace(".", "-dot-").lower()
        )
        connection.execute(
            t_workspaces.insert().values(
                pvc_name=pvc_name,
                size="20Gi",
                user_id=user["id"],
            )
        )
