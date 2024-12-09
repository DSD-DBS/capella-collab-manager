# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove jenkins support

Revision ID: a81a79a7eaac
Revises: a6aedef45374
Create Date: 2022-10-07 10:29:25.859413

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a81a79a7eaac"
down_revision = "d64fc5a97252"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_jenkins_id", table_name="jenkins")
    op.drop_table("jenkins")
