# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels import (
    injectables as toolmodels_injectables,
)
from capellacollab.projects.toolmodels import models as toolmodels_models

from . import crud, exceptions, models


def get_existing_t4c_model(
    t4c_model_id: int,
    capella_model: t.Annotated[
        toolmodels_models.DatabaseToolModel,
        fastapi.Depends(toolmodels_injectables.get_existing_capella_model),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabaseT4CModel:
    if not (t4c_model := crud.get_t4c_model_by_id(db, t4c_model_id)):
        raise exceptions.T4CIntegrationNotFoundError(t4c_model_id)
    if t4c_model.model.id != capella_model.id:
        raise exceptions.T4CIntegrationDoesntBelongToModel(
            t4c_model_id, capella_model.slug
        )
    return t4c_model
