# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""add readonly docker image

Revision ID: ab01ad045341
Revises: fdff657f3cc1
Create Date: 2022-10-13 10:51:57.631309

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ab01ad045341"
down_revision = "fdff657f3cc1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tools",
        sa.Column(
            "readonly_docker_image_template", sa.String(), nullable=True
        ),
    )


def downgrade():
    with op.batch_alter_table("tools") as batch_op:
        batch_op.drop_column("readonly_docker_image_template")
