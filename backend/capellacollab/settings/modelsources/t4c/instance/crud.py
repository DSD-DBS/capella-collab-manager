# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

from . import models


def get_t4c_instances(
    db: orm.Session,
) -> abc.Sequence[models.DatabaseT4CInstance]:
    return db.execute(sa.select(models.DatabaseT4CInstance)).scalars().all()


def get_t4c_instances_by_version(
    db: orm.Session, version_id: int
) -> abc.Sequence[models.DatabaseT4CInstance]:
    return (
        db.execute(
            sa.select(models.DatabaseT4CInstance).where(
                models.DatabaseT4CInstance.version_id == version_id
            )
        )
        .scalars()
        .all()
    )


def get_t4c_instance_by_id(
    db: orm.Session, instance_id: int
) -> models.DatabaseT4CInstance | None:
    return db.execute(
        sa.select(models.DatabaseT4CInstance).where(
            models.DatabaseT4CInstance.id == instance_id
        )
    ).scalar_one_or_none()


def get_t4c_instance_by_name(
    db: orm.Session, instance_name: str
) -> models.DatabaseT4CInstance | None:
    return db.execute(
        sa.select(models.DatabaseT4CInstance).where(
            models.DatabaseT4CInstance.name == instance_name
        )
    ).scalar_one_or_none()


def create_t4c_instance(
    db: orm.Session, instance: models.DatabaseT4CInstance
) -> models.DatabaseT4CInstance:
    db.add(instance)
    db.commit()
    return instance


def update_t4c_instance(
    db: orm.Session,
    instance: models.DatabaseT4CInstance,
    patch_t4c_instance: models.PatchT4CInstance,
):
    if patch_t4c_instance.password == "":
        patch_t4c_instance.password = None
    database.patch_database_with_pydantic_object(instance, patch_t4c_instance)

    db.commit()

    return instance


def delete_t4c_instance(
    db: orm.Session,
    instance: models.DatabaseT4CInstance,
):
    db.delete(instance)
    db.commit()
