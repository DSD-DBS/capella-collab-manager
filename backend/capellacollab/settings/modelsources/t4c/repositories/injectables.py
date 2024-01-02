# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.settings.modelsources.t4c import (
    injectables as settings_t4c_injectables,
)
from capellacollab.settings.modelsources.t4c import (
    models as settings_t4c_models,
)

from . import crud, models


def get_existing_t4c_repository(
    t4c_repository_id: int,
    db: orm.Session = fastapi.Depends(database.get_db),
    instance: settings_t4c_models.DatabaseT4CInstance = fastapi.Depends(
        settings_t4c_injectables.get_existing_instance
    ),
) -> models.DatabaseT4CRepository:
    if repository := crud.get_t4c_repository_by_id(db, t4c_repository_id):
        if repository.instance != instance:
            raise fastapi.HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "reason": f"Repository {repository.name} is not part of the instance {instance.name}."
                },
            )
        return repository

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"Repository with id {t4c_repository_id} was not found."
        },
    )
