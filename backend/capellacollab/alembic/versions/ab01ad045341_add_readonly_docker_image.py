# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""add readonly docker image

Revision ID: ab01ad045341
Revises: b14f7a53b9e2
Create Date: 2022-10-13 10:51:57.631309

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ab01ad045341"
down_revision = "b14f7a53b9e2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tools",
        sa.Column(
            "readonly_docker_image_template", sa.String(), nullable=True
        ),
    )
