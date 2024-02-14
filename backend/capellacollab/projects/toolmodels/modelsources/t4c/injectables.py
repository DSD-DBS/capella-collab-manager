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


def get_existing_t4c_model(
    t4c_model_id: int,
    capella_model: toolmodels_models.DatabaseToolModel = fastapi.Depends(
        toolmodels_injectables.get_existing_capella_model
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabaseT4CModel:
    if not (t4c_model := crud.get_t4c_model_by_id(db, t4c_model_id)):
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The TeamForCapella model with the id {t4c_model_id} was not found.",
            },
        )
    if t4c_model.model.id != capella_model.id:
        raise fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "reason": f"The TeamForCapella model with the id {t4c_model_id} doesn't belong to the model '{capella_model.slug}'.",
            },
        )
    return t4c_model
