# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Update indexes for models

Revision ID: b036c613afc7
Revises: a81a79a7eaac
Create Date: 2022-10-07 11:10:08.420400

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "b036c613afc7"
down_revision = "a81a79a7eaac"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("ix_capella_models_id", table_name="models")
    op.drop_index("ix_capella_models_name", table_name="models")
    op.create_index(op.f("ix_models_id"), "models", ["id"], unique=True)
    op.create_index(op.f("ix_models_name"), "models", ["name"], unique=False)
