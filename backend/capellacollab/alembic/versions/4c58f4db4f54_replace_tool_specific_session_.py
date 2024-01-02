# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Replace tool specific session attributes with environment

Revision ID: 4c58f4db4f54
Revises: 97c7acd616fc
Create Date: 2023-08-07 20:09:26.524318

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "4c58f4db4f54"
down_revision = "97c7acd616fc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "sessions",
        sa.Column(
            "environment",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    t_sessions = sa.Table(
        "sessions", sa.MetaData(), autoload_with=op.get_bind()
    )

    sessions = op.get_bind().execute(sa.select(t_sessions))
    for session in sessions:
        op.get_bind().execute(
            sa.update(t_sessions)
            .where(t_sessions.c.id == session.id)
            .values(
                environment={
                    "JUPYTER_TOKEN": session.jupyter_token,
                    "T4C_PASSWORD": session.t4c_password,
                }
            )
        )
    op.drop_column("sessions", "mac")
    op.drop_column("sessions", "jupyter_token")
    op.drop_column("sessions", "t4c_password")
