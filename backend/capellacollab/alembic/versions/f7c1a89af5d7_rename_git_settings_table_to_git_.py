# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Rename git_settings table to git_instances

Revision ID: f7c1a89af5d7
Revises: 5717cf6b004d
Create Date: 2023-02-10 09:32:05.903031

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f7c1a89af5d7"
down_revision = "5717cf6b004d"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("git_settings", "git_instances")
    op.execute(
        sa.text(
            "ALTER SEQUENCE git_settings_id_seq RENAME TO git_instances_id_seq"
        )
    )
    op.execute(
        sa.text("ALTER INDEX git_settings_pkey RENAME TO git_instances_pkey")
    )
