# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove scope from notices

Revision ID: 6c5d1334d606
Revises: 740f45fd20e8
Create Date: 2022-10-14 08:17:28.933231

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6c5d1334d606"
down_revision = "740f45fd20e8"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("notices", "scope")
