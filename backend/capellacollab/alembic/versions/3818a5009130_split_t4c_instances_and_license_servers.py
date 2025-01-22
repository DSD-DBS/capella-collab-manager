# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Split T4C Instances and License Servers

Revision ID: 3818a5009130
Revises: 7cf3357ddd7b
Create Date: 2024-10-01 15:46:26.054936

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3818a5009130"
down_revision = "7cf3357ddd7b"
branch_labels = None
depends_on = None

t_tool_versions = sa.Table(
    "versions",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("name", sa.String()),
)

t_t4c_instances_old = sa.Table(
    "t4c_instances",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("usage_api", sa.String()),
    sa.Column("license", sa.String()),
)


t_t4c_instances_new = sa.Table(
    "t4c_instances",
    sa.MetaData(),
    sa.Column("id", sa.Integer()),
    sa.Column("license_server_id", sa.Integer()),
)


def upgrade():
    t_license_servers = op.create_table(
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

    bind = op.get_bind()
    t4c_instances = (
        bind.execute(sa.select(t_t4c_instances_old)).mappings().all()
    )

    grouped_instances: dict[tuple[str, str], list[int]] = {}
    for instance in t4c_instances:
        key = (instance.usage_api, instance.license)
        if key not in grouped_instances:
            grouped_instances[key] = []
        grouped_instances[key].append(instance.id)

    # Create new license_server for each group and associate with instances
    for idx, ((usage_api, license_key), instance_ids) in enumerate(
        grouped_instances.items()
    ):
        license_server_id = bind.execute(
            t_license_servers.insert()
            .values(
                name=f"License server {idx + 1}",
                usage_api=usage_api,
                license_key=license_key,
            )
            .returning(t_license_servers.c.id)
        ).scalar()

        for instance_id in instance_ids:
            bind.execute(
                sa.update(t_t4c_instances_new)
                .where(t_t4c_instances_new.c.id == instance_id)
                .values(license_server_id=license_server_id)
            )

    op.alter_column("t4c_instances", "license_server_id", nullable=False)
    op.drop_column("t4c_instances", "license")
    op.drop_column("t4c_instances", "usage_api")
