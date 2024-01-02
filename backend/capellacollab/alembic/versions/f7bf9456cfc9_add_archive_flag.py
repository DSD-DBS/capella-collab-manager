# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add archive flag

Revision ID: f7bf9456cfc9
Revises: c9f30ccd4650
Create Date: 2023-08-28 08:57:22.931913

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f7bf9456cfc9"
down_revision = "c9f30ccd4650"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "t4c_instances", sa.Column("is_archived", sa.Boolean(), nullable=True)
    )

    op.get_bind().execute(
        sa.text("UPDATE t4c_instances SET is_archived=false")
    )

    op.alter_column(
        "t4c_instances",
        "is_archived",
        existing_type=sa.BOOLEAN(),
        nullable=False,
    )
