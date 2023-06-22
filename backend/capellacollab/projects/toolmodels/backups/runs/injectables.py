# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels.backups import (
    injectables as backups_injectables,
)
from capellacollab.projects.toolmodels.backups import models as backups_models

from . import crud


def get_existing_pipeline_run(
    pipeline_run_id: int,
    pipeline: backups_models.DatabaseBackup = fastapi.Depends(
        backups_injectables.get_existing_pipeline
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> backups_models.DatabaseBackup:
    if pipeline_run := crud.get_pipeline_run_by_id(db, pipeline_run_id):
        if pipeline_run.pipeline.id != pipeline.id:
            raise fastapi.HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "reason": f"The pipeline run with the id {pipeline_run.id} does not belong to the pipeline with id {pipeline.id}.",
                },
            )
        return pipeline_run
    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The pipeline run with the id {pipeline_run_id} was not found.",
        },
    )
