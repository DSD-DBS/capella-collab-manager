# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.modelsources.t4c import crud
from capellacollab.projects.capellamodels.modelsources.t4c.models import (
    DatabaseT4CModel,
)


def get_existing_t4c_model(
    t4c_model_id: int, db: Session = Depends(get_db)
) -> DatabaseT4CModel:
    return crud.get_t4c_model_by_id(db, t4c_model_id)
