# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from capellacollab.core.database import get_db
from capellacollab.projects.capellamodels.backups.models import DB_EASEBackup
from capellacollab.projects.capellamodels.injectables import (
    get_existing_capella_model,
)
from capellacollab.projects.capellamodels.models import DatabaseCapellaModel

from . import crud


def get_existing_pipeline(
    pipeline_id: int,
    model: DatabaseCapellaModel = Depends(get_existing_capella_model),
    db: Session = Depends(get_db),
) -> DB_EASEBackup:
    try:
        return crud.get_pipeline_by_id(db, pipeline_id)
    except NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The pipeline with the id {pipeline_id} of the model with th id {model.id} was not found.",
            },
        )


def get_existing_pipeline_run(
    run_id: int,
    pipeline: DB_EASEBackup = Depends(get_existing_pipeline),
    db: Session = Depends(get_db),
):
    try:
        return crud.get_pipeline_run_by_id(db, pipeline, run_id)
    except NoResultFound:
        raise HTTPException(
            404,
            {
                "reason": f"The pipeline run with the id {run_id} of the pipeline with th id {pipeline.id} was not found.",
            },
        )
