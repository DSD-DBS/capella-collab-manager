# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

import capellacollab.projects.toolmodels.backups.injectables as backups_injectables
import capellacollab.projects.toolmodels.backups.models as backups_models
from capellacollab.core.database import get_db
from capellacollab.projects.toolmodels.backups.models import DatabaseBackup

from . import crud


def get_existing_pipeline_run(
    pipeline_run_id: int,
    pipeline: backups_models.DatabaseBackup = Depends(
        backups_injectables.get_existing_pipeline
    ),
    db: Session = Depends(get_db),
) -> DatabaseBackup:
    if pipeline_run := crud.get_pipeline_run_by_id(db, pipeline_run_id):
        if pipeline_run.pipeline.id != pipeline.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "reason": f"The pipeline run with the id {pipeline_run.id} does not belong to the pipeline with id {pipeline.id}.",
                },
            )
        return pipeline_run
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The pipeline run with the id {pipeline_run_id} was not found.",
        },
    )
