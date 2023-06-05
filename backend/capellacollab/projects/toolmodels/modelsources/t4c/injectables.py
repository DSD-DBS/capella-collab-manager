# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel
from capellacollab.projects.toolmodels.modelsources.t4c import crud
from capellacollab.projects.toolmodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)


def get_existing_t4c_model(
    t4c_model_id: int,
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseT4CModel:
    if not (t4c_model := crud.get_t4c_model_by_id(db, t4c_model_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            {
                "reason": f"The TeamForCapella model with the id {t4c_model_id} was not found.",
            },
        )
    if t4c_model.model.id != capella_model.id:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            {
                "reason": f"The TeamForCapella model with the id {t4c_model_id} doesn't belong to the model '{capella_model.slug}'.",
            },
        )
    return t4c_model
