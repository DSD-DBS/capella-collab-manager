# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Link Git Repositories with Projects

Revision ID: 377b60de4441
Revises: 6a8bdec1dccb
Create Date: 2021-09-03 12:58:16.636950

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "377b60de4441"
down_revision = "6a8bdec1dccb"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "git_models", sa.Column("project_name", sa.String(), nullable=False)
    )
    op.create_foreign_key(
        None, "git_models", "projects", ["project_name"], ["name"]
    )
