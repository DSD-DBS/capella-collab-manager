# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add read/write access

Revision ID: f3efdcedfdde
Revises: d3c85f34aae6
Create Date: 2021-08-24 12:43:46.471793

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f3efdcedfdde"
down_revision = "d3c85f34aae6"
branch_labels = None
depends_on = None


def upgrade():
    repositoryuserpermission = postgresql.ENUM(
        "READ", "WRITE", name="repositoryuserpermission"
    )
    repositoryuserpermission.create(op.get_bind())

    op.add_column(
        "repository_user_association",
        sa.Column(
            "permission",
            sa.Enum("READ", "WRITE", name="repositoryuserpermission"),
            nullable=True,
        ),
    )
    op.execute(
        sa.text("UPDATE repository_user_association SET permission='WRITE'")
    )
    op.alter_column(
        "repository_user_association", "permission", nullable=False
    )
