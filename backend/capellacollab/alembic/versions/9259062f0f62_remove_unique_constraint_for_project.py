# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove unique constraint for project

Revision ID: 9259062f0f62
Revises: f3ed32b2cfb0
Create Date: 2021-09-07 18:19:57.816445

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9259062f0f62"
down_revision = "f3ed32b2cfb0"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_projects_name", table_name="projects")
