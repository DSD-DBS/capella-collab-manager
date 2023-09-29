# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add project archive flag

Revision ID: ac0e6e0f77ee
Revises: 1a4208c18909
Create Date: 2023-09-25 16:08:07.115693

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ac0e6e0f77ee"
down_revision = "1a4208c18909"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "projects", sa.Column("is_archived", sa.Boolean(), nullable=True)
    )

    op.get_bind().execute(sa.text("UPDATE projects SET is_archived=false"))

    op.alter_column(
        "projects", "is_archived", existing_type=sa.BOOLEAN(), nullable=False
    )
