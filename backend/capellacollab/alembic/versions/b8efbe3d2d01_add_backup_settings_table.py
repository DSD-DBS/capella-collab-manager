# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add backup settings table

Revision ID: b8efbe3d2d01
Revises: df07aad6525d
Create Date: 2022-11-07 16:23:04.837964

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from capellacollab.config import config

# revision identifiers, used by Alembic.
revision = "b8efbe3d2d01"
down_revision = "df07aad6525d"
branch_labels = None
depends_on = None


def upgrade():
    setting_backups_table = op.create_table(
        "settings_backups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("docker_image", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_settings_backups_id"),
        "settings_backups",
        ["id"],
        unique=False,
    )

    op.bulk_insert(
        setting_backups_table,
        [
            {
                "docker_image": config["docker"]["registry"]
                + "/t4c/client/backup:5.2-latest",
            }
        ],
    )


def downgrade():
    op.drop_index(
        op.f("ix_settings_backups_id"), table_name="settings_backups"
    )
    op.drop_table("settings_backups")
