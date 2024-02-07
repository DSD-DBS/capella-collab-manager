# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models

from . import crud, models


def get_existing_pipeline(
    pipeline_id: int,
    model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseBackup:
    if backup := crud.get_pipeline_by_id(db, pipeline_id):
        return backup

    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The pipeline with the ID {pipeline_id} of the model with the name '{model.name}' was not found.",
        },
    )
