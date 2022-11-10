# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Add tool and version to sessions table

Revision ID: b14f7a53b9e2
Revises: 598efe35c2de
Create Date: 2022-11-10 08:19:53.488507

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b14f7a53b9e2"
down_revision = "598efe35c2de"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions", sa.Column("tool_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "sessions", sa.Column("version_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(None, "sessions", "versions", ["version_id"], ["id"])
    op.create_foreign_key(None, "sessions", "tools", ["tool_id"], ["id"])


def downgrade():
    op.drop_constraint("sessions_tool_id_fkey", "sessions", type_="foreignkey")
    op.drop_constraint(
        "sessions_version_id_fkey", "sessions", type_="foreignkey"
    )
    op.drop_column("sessions", "version_id")
    op.drop_column("sessions", "tool_id")
