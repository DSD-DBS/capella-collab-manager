# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add IdP identifier and email columns

Revision ID: 028c72ddfd20
Revises: a1e59021e0d0
Create Date: 2024-07-22 14:49:47.575605

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "028c72ddfd20"
down_revision = "a1e59021e0d0"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("idp_identifier", sa.String(), nullable=True)
    )

    t_users = sa.Table("users", sa.MetaData(), autoload_with=op.get_bind())

    users = op.get_bind().execute(sa.select(t_users))
    for user in users:
        op.get_bind().execute(
            sa.update(t_users)
            .where(t_users.c.id == user.id)
            .values(idp_identifier=user.name)
        )

    op.alter_column("users", "idp_identifier", nullable=False)

    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(
        op.f("ix_users_idp_identifier"),
        "users",
        ["idp_identifier"],
        unique=True,
    )
