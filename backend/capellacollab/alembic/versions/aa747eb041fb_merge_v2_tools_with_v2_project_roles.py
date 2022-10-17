# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Merge v2/tools with v2/project-roles

Revision ID: aa747eb041fb
Revises: 3fa75ddfdde8, 6c5d1334d606
Create Date: 2022-10-17 16:49:03.958375

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "aa747eb041fb"
down_revision = ("3fa75ddfdde8", "6c5d1334d606")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
