# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.settings.modelsources.t4c.models import DatabaseT4CInstance
from capellacollab.settings.modelsources.t4c.repositories.models import (
    CreateT4CRepository,
    DatabaseT4CRepository,
)


def get_t4c_repository(id_: int, db: Session) -> DatabaseT4CRepository:
    return db.execute(
        select(DatabaseT4CRepository).where(DatabaseT4CRepository.id == id_)
    ).scalar_one()


def create_t4c_repository(
    repository: CreateT4CRepository, instance: DatabaseT4CInstance, db: Session
):
    repository = DatabaseT4CRepository(name=repository.name)
    repository.instance = instance
    db.add(repository)
    db.commit()
    db.refresh(repository)
    return repository


def delete_4c_repository(
    repository: DatabaseT4CRepository, db: Session
) -> None:
    db.delete(repository)
    db.commit()
