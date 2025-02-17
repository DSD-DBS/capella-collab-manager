# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.settings.modelsources.t4c.instance import (
    crud,
    exceptions,
    models,
)


def get_existing_instance(
    t4c_instance_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseT4CInstance:
    if t4c_instance := crud.get_t4c_instance_by_id(db, t4c_instance_id):
        return t4c_instance

    raise exceptions.T4CInstanceNotFoundError(t4c_instance_id)


def get_existing_unarchived_instance(
    t4c_instance_id: int,
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
):
    t4c_instance = get_existing_instance(t4c_instance_id, db)
    if t4c_instance.is_archived:
        raise exceptions.T4CInstanceIsArchivedError(t4c_instance.id)

    return t4c_instance
