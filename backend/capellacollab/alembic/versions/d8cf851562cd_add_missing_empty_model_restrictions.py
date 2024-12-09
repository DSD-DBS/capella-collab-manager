# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add missing empty model restrictions

Revision ID: d8cf851562cd
Revises: 4c58f4db4f54
Create Date: 2023-08-21 15:45:27.243037

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "d8cf851562cd"
down_revision = "4c58f4db4f54"
branch_labels = None
depends_on = None


def upgrade():
    t_restrictions = sa.Table(
        "model_restrictions", sa.MetaData(), autoload_with=op.get_bind()
    )

    restrictions_model_ids = (
        op.get_bind()
        .execute(sa.text("SELECT model_id FROM model_restrictions"))
        .scalars()
        .all()
    )
    models_ids = (
        op.get_bind().execute(sa.text("SELECT id FROM models")).scalars().all()
    )

    model_ids_restrictions_null = set(models_ids) - set(restrictions_model_ids)

    for model_id in model_ids_restrictions_null:
        op.get_bind().execute(
            t_restrictions.insert().values(
                model_id=model_id, allow_pure_variants=False
            )
        )
