# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""make instance name unique

Revision ID: f55b41e32223
Revises: 0e2028f83156
Create Date: 2023-12-12 18:01:35.967370

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f55b41e32223"
down_revision = "0e2028f83156"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(None, "t4c_instances", ["name"])
