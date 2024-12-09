# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove table for docker images

Revision ID: 740f45fd20e8
Revises: 3fe3ed1167fb
Create Date: 2022-10-14 08:16:20.665269

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "740f45fd20e8"
down_revision = "3fe3ed1167fb"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index(
        "ix_config_dockerimages_id", table_name="config_dockerimages"
    )
    op.drop_table("config_dockerimages")
