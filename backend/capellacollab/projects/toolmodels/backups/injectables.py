# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.toolmodels.backups.models import DatabaseBackup
from capellacollab.projects.toolmodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.toolmodels.models import DatabaseCapellaModel

from . import crud


def get_existing_pipeline(
    pipeline_id: int,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DatabaseBackup:
    if not (backup := crud.get_pipeline_by_id(db, pipeline_id)):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            {
                "reason": f"The pipeline with the id {pipeline_id} of the model with th id {model.id} was not found.",
            },
        )
    return backup
