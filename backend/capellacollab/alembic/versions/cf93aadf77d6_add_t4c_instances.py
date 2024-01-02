# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add T4C Instances

Revision ID: cf93aadf77d6
Revises: d64fc5a97252
Create Date: 2022-09-29 11:52:20.442558

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "cf93aadf77d6"
down_revision = "d64fc5a97252"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "t4c_instances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=True),
        sa.Column("license", sa.String(), nullable=True),
        sa.Column("host", sa.String(), nullable=True),
        sa.Column("port", sa.Integer(), nullable=False, server_default="2036"),
        sa.Column("usage_api", sa.String(), nullable=True),
        sa.Column("rest_api", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("password", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["version_id"],
            ["versions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_t4c_instances_id"), "t4c_instances", ["id"], unique=False
    )
