# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from requests import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from capellacollab.settings.modelsources.t4c.models import (
    CreateT4CInstance,
    DatabaseT4CInstance,
)


def get_all_t4c_instances(db: Session) -> list[DatabaseT4CInstance]:
    return db.execute(select(DatabaseT4CInstance)).scalars().all()


def get_t4c_instance(id_: int, db: Session) -> DatabaseT4CInstance:
    return db.execute(
        select(DatabaseT4CInstance).where(DatabaseT4CInstance.id == id_)
    ).scalar_one()


def create_t4c_instance(instance: CreateT4CInstance, db: Session):
    request = Request("GET", instance.rest_api)
    request.prepare()
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def update_t4c_instance(instance: DatabaseT4CInstance, db: Session):
    request = Request("GET", instance.rest_api)
    request.prepare()
    db.add(instance)
    db.commit()
    return instance
