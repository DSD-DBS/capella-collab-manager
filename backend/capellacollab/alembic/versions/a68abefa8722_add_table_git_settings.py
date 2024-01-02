# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add table git_settings

Revision ID: a68abefa8722
Revises: 703517ca79bc
Create Date: 2022-07-22 11:27:32.428542

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a68abefa8722"
down_revision = "703517ca79bc"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "git_settings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column(
            "type",
            sa.Enum(
                "GENERAL", "GITLAB", "GITHUB", "AZUREDEVOPS", name="gittype"
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_git_settings_id"), "git_settings", ["id"], unique=False
    )
