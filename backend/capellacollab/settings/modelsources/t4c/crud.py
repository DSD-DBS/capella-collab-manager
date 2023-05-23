# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.core.database import patch_database_with_pydantic_object
from capellacollab.settings.modelsources.t4c.models import (
    DatabaseT4CInstance,
    PatchT4CInstance,
)


def get_t4c_instances(db: Session) -> Sequence[DatabaseT4CInstance]:
    return db.execute(select(DatabaseT4CInstance)).scalars().all()


def get_t4c_instances_by_version(
    db: Session, version_id: int
) -> Sequence[DatabaseT4CInstance]:
    return (
        db.execute(
            select(DatabaseT4CInstance).where(
                DatabaseT4CInstance.version_id == version_id
            )
        )
        .scalars()
        .all()
    )


def get_t4c_instance_by_id(
    db: Session, instance_id: int
) -> DatabaseT4CInstance | None:
    return db.execute(
        select(DatabaseT4CInstance).where(
            DatabaseT4CInstance.id == instance_id
        )
    ).scalar_one_or_none()


def create_t4c_instance(
    db: Session, instance: DatabaseT4CInstance
) -> DatabaseT4CInstance:
    db.add(instance)
    db.commit()
    return instance


def update_t4c_instance(
    db: Session,
    instance: DatabaseT4CInstance,
    patch_t4c_instance: PatchT4CInstance,
):
    patch_database_with_pydantic_object(instance, patch_t4c_instance)

    db.commit()
    return instance
