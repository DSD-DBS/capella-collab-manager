# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Split T4C Instances and License Servers

Revision ID: 3818a5009130
Revises: 7cf3357ddd7b
Create Date: 2024-10-01 15:46:26.054936

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = "3818a5009130"
down_revision = "7cf3357ddd7b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "t4c_license_servers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("usage_api", sa.String(), nullable=False),
        sa.Column("license_key", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_t4c_license_servers_id"),
        "t4c_license_servers",
        ["id"],
        unique=True,
    )
    op.add_column(
        "t4c_instances",
        sa.Column("license_server_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        None,
        "t4c_instances",
        "t4c_license_servers",
        ["license_server_id"],
        ["id"],
    )

    # Fetch existing t4c_instances and group by usage_api and license
    bind = op.get_bind()
    session = Session(bind=bind)
    t4c_instances = session.execute(
        sa.text("SELECT id, usage_api, license FROM t4c_instances")
    ).fetchall()

    grouped_instances = {}
    for instance in t4c_instances:
        key = (instance.usage_api, instance.license)
        if key not in grouped_instances:
            grouped_instances[key] = []
        grouped_instances[key].append(instance.id)

    # Create new license_server for each group and associate with instances
    for (usage_api, license_key), instance_ids in grouped_instances.items():
        license_server_id = session.execute(
            sa.text(
                "INSERT INTO t4c_license_servers (name, usage_api, license_key) VALUES (:name, :usage_api, :license_key) RETURNING id"
            ),
            {
                "name": usage_api,
                "usage_api": usage_api,
                "license_key": license_key,
            },
        ).scalar()

        session.execute(
            sa.text(
                "UPDATE t4c_instances SET license_server_id = :license_server_id WHERE id = ANY(:instance_ids)"
            ),
            {
                "license_server_id": license_server_id,
                "instance_ids": instance_ids,
            },
        )

    session.commit()

    op.alter_column("t4c_instances", "license_server_id", nullable=False)
    op.drop_column("t4c_instances", "license")
    op.drop_column("t4c_instances", "usage_api")
