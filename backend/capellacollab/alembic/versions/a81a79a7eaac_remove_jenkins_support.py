# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove jenkins support

Revision ID: a81a79a7eaac
Revises: a6aedef45374
Create Date: 2022-10-07 10:29:25.859413

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a81a79a7eaac"
down_revision = "a6aedef45374"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_jenkins_id", table_name="jenkins")
    op.drop_table("jenkins")


def downgrade():
    op.create_table(
        "jenkins",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "git_model_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["git_model_id"],
            ["git_models.id"],
            name="jenkins_git_model_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", "git_model_id", name="jenkins_pkey"),
    )
    op.create_index("ix_jenkins_id", "jenkins", ["id"], unique=False)
