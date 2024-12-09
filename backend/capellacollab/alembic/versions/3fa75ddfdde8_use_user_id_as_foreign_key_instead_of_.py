# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Use user id as foreign key (instead of username)

Revision ID: 3fa75ddfdde8
Revises: 3fe3ed1167fb
Create Date: 2022-10-17 14:08:01.431956

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3fa75ddfdde8"
down_revision = "6c5d1334d606"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "project_user_association",
        sa.Column("user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        None, "project_user_association", "users", ["user_id"], ["id"]
    )

    t_users = sa.Table("users", sa.MetaData(), autoload_with=op.get_bind())

    t_project_user_association = sa.Table(
        "project_user_association", sa.MetaData(), autoload_with=op.get_bind()
    )

    users = op.get_bind().execute(sa.select(t_users))
    for user in users:
        op.get_bind().execute(
            sa.update(t_project_user_association)
            .where(t_project_user_association.c.username == user.name)
            .values(user_id=user.id)
        )
    op.alter_column(
        "project_user_association",
        "user_id",
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
    op.drop_constraint(
        "project_user_association_username_fkey",
        "project_user_association",
        type_="foreignkey",
    )
    op.drop_column("project_user_association", "username")
