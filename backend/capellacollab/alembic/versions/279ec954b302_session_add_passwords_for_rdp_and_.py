# Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""session: add passwords for rdp and guacamole

Revision ID: 279ec954b302
Revises: 
Create Date: 2021-08-12 23:01:08.764707

"""
# 3rd party:
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "279ec954b302"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("sessions", sa.Column("rdp_password", sa.String(), nullable=True))
    op.add_column(
        "sessions", sa.Column("guacamole_password", sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column("sessions", "guacamole_password")
    op.drop_column("sessions", "rdp_password")
