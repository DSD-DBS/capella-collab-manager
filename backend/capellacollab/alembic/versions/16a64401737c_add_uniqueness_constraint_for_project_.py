# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

"""Add uniqueness constraint for project users

Revision ID: 16a64401737c
Revises: 8731ac0b284e
Create Date: 2025-02-10 16:19:52.570927

"""

import logging

import sqlalchemy as sa
from alembic import op

LOGGER = logging.getLogger(__name__)

# revision identifiers, used by Alembic.
revision = "16a64401737c"
down_revision = "8731ac0b284e"
branch_labels = None
depends_on = None

t_project_user_association = sa.Table(
    "project_user_association",
    sa.MetaData(),
    sa.Column("user_id", sa.Integer),
    sa.Column("project_id", sa.Integer),
    sa.Column("role", sa.String),
    sa.Column("permission", sa.String),
)


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    constraint = insp.get_pk_constraint("project_user_association")

    if (
        constraint["name"]
        and constraint["name"] == "project_user_association_pkey"
    ):
        # The database looks correct, nothing to do
        return

    project_user_combinations = []
    users_to_create = {}

    for project_user in (
        bind.execute(sa.select(t_project_user_association)).mappings().all()
    ):
        project_user_tuple = (
            project_user["user_id"],
            project_user["project_id"],
        )
        if project_user_tuple in project_user_combinations:
            # User is part of the project multiple times

            LOGGER.info("Found duplicated user %s", project_user_tuple)

            bind.execute(
                sa.delete(t_project_user_association)
                .where(
                    t_project_user_association.c.user_id
                    == project_user["user_id"]
                )
                .where(
                    t_project_user_association.c.project_id
                    == project_user["project_id"]
                )
            )
            users_to_create[project_user_tuple] = project_user
        else:
            project_user_combinations.append(project_user_tuple)

    for user in users_to_create.values():
        LOGGER.info("Recreating user: %s", user)
        bind.execute(
            t_project_user_association.insert().values(
                user_id=user["user_id"],
                project_id=user["project_id"],
                role=user["role"],
                permission=user["permission"],
            )
        )

    LOGGER.info("Creating primary key 'project_user_association_pkey'")
    op.create_primary_key(
        "project_user_association_pkey",
        "project_user_association",
        ["user_id", "project_id"],
    )
