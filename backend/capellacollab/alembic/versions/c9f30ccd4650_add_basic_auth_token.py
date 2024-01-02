# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add basic auth token

Revision ID: c9f30ccd4650
Revises: 1a4208c18909
Create Date: 2023-09-06 14:42:53.016924

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c9f30ccd4650"
down_revision = "1a4208c18909"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "basic_auth_token",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("hash", sa.String(), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_basic_auth_token_id"),
        "basic_auth_token",
        ["id"],
        unique=False,
    )
