# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Merge branches permissions and guacamole-rework

Revision ID: c926d3e402a8
Revises: 1b4c1dc944d6, 52aec4f341a5
Create Date: 2021-08-30 12:27:00.888738

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c926d3e402a8"
down_revision = ("1b4c1dc944d6", "52aec4f341a5")
branch_labels = None
depends_on = None


def upgrade():
    pass
