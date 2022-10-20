# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Merge v2/tools with v2/staging

Revision ID: 7d15f1d0b7d6
Revises: aa747eb041fb, 24fd3c70bacf
Create Date: 2022-10-20 11:47:11.202482

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "7d15f1d0b7d6"
down_revision = ("aa747eb041fb", "24fd3c70bacf")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
