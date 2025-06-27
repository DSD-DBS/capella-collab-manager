# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Update pipelines for scheduling

Revision ID: 53b8f1f94922
Revises: 169c90c7eff1
Create Date: 2025-06-27 14:56:02.952043

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "53b8f1f94922"
down_revision = "169c90c7eff1"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("backups", "include_commit_history")
    op.drop_column("backups", "k8s_cronjob_id")
    op.alter_column(
        "pipeline_run",
        "triggerer_id",
        existing_type=sa.INTEGER(),
        nullable=True,
    )
