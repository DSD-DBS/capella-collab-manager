# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel
from capellacollab.projects.capellamodels.modelsources.t4c import crud
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)


def get_existing_t4c_model(
    t4c_model_id: int,
    capella_model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseT4CModel:
    try:
        t4c_model = crud.get_t4c_model_by_id(db, t4c_model_id)
        if t4c_model.model_id == capella_model.id:
            return t4c_model

    except NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The t4c model ({t4c_model_id}) does not exists on the capella model with the ID {capella_model}."
            },
        )
