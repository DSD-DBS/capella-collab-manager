# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""rename tpye_id to nature_id

Revision ID: 8eceebe9b3ea
Revises: e7a140389e22
Create Date: 2022-10-28 14:22:52.516394

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "8eceebe9b3ea"
down_revision = "e7a140389e22"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("models", "type_id", new_column_name="nature_id")
    op.drop_constraint("models_type_id_fkey", "models", type_="foreignkey")
    op.create_foreign_key(None, "models", "types", ["nature_id"], ["id"])
