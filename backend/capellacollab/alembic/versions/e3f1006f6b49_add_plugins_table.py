# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add plugins table

Revision ID: e3f1006f6b49
Revises: d0cbf2813066
Create Date: 2023-05-26 11:56:13.928534

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e3f1006f6b49"
down_revision = "ac0e6e0f77ee"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plugins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.Column("remote", sa.String(), nullable=False),
        sa.Column(
            "content", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plugins_id"), "plugins", ["id"], unique=True)
