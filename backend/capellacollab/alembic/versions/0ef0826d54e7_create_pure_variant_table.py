# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Create pure::variant table.

Revision ID: 0ef0826d54e7
Revises: 7617cde6fbb1
Create Date: 2022-11-18 11:40:46.395645

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0ef0826d54e7"
down_revision = "7617cde6fbb1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pure_variants_license",
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("value"),
    )


def downgrade():
    op.drop_table("pure_variants_license")
