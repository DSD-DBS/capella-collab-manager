# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Remove outdated model type

Revision ID: 9960cd073b98
Revises: cf93aadf77d6
Create Date: 2022-10-06 08:52:02.263343

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9960cd073b98"
down_revision = "cf93aadf77d6"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("models", "model_type")
