# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from sqlalchemy import orm

from capellacollab.core import database

from .. import injectables as settings_t4c_injectables
from .. import models as settings_t4c_models
from . import crud, exceptions, models


def get_existing_t4c_repository(
    t4c_repository_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
) -> models.DatabaseT4CRepository:
    if repository := crud.get_t4c_repository_by_id(db, t4c_repository_id):
        if repository.instance != instance:
            raise exceptions.T4CRepositoryDoesntBelongToServerError(
                repository_id=t4c_repository_id, server_id=instance.id
            )
        return repository

    raise exceptions.T4CRepositoryNotFoundError(t4c_repository_id)
