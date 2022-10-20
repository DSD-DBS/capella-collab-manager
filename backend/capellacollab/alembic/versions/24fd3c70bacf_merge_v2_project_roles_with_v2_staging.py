# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Merge v2/project-roles with v2/staging

Revision ID: 24fd3c70bacf
Revises: 3fa75ddfdde8, 5a6b36abdf25
Create Date: 2022-10-20 09:16:39.077107

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "24fd3c70bacf"
down_revision = ("3fa75ddfdde8", "5a6b36abdf25")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
