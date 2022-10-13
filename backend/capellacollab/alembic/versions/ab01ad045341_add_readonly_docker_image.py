# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

"""add readonly docker image

Revision ID: ab01ad045341
Revises: 24fd3c70bacf
Create Date: 2022-10-13 10:51:57.631309

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ab01ad045341"
down_revision = "24fd3c70bacf"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tools") as batch_op:
        batch_op.add_column(
            sa.Column(
                "readonly_docker_image_template", sa.String(), nullable=True
            )
        )


def downgrade():
    with op.batch_alter_table("tools") as batch_op:
        batch_op.drop_column("readonly_docker_image_template")
