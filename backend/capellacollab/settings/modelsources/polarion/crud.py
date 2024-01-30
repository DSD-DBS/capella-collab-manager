# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from collections import abc

import sqlalchemy as sa
from sqlalchemy import orm

from capellacollab.core import database

from . import models


def get_polarion_instances(
    db: orm.Session,
) -> abc.Sequence[models.DatabasePolarionInstance]:
    return (
        db.execute(sa.select(models.DatabasePolarionInstance)).scalars().all()
    )


def get_polarion_instance_by_id(
    db: orm.Session, polarion_instance_id: int
) -> models.DatabasePolarionInstance | None:
    return db.execute(
        sa.select(models.DatabasePolarionInstance).where(
            models.DatabasePolarionInstance.id == polarion_instance_id
        )
    ).scalar_one_or_none()


def create_polarion_instance(
    db: orm.Session, body: models.PolarionInstance
) -> models.DatabasePolarionInstance:
    polarion_instance = models.DatabasePolarionInstance(
        name=body.name,
        url=body.url,
    )

    db.add(polarion_instance)
    db.commit()
    return polarion_instance


def update_polarion_instance(
    db: orm.Session,
    polarion_instance: models.DatabasePolarionInstance,
    post_polarion_instance: models.PolarionInstance,
) -> models.DatabasePolarionInstance:
    database.patch_database_with_pydantic_object(
        polarion_instance, post_polarion_instance
    )

    db.commit()
    return polarion_instance


def delete_polarion_instance(
    db: orm.Session, polarion_instance: models.DatabasePolarionInstance
) -> None:
    db.delete(polarion_instance)
    db.commit()
