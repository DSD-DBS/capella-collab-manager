# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
from fastapi import status
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels.backups import (
    injectables as backups_injectables,
)
from capellacollab.projects.toolmodels.backups import models as backups_models

from . import crud, models


def get_existing_pipeline_run(
    pipeline_run_id: int,
    pipeline: backups_models.DatabaseBackup = fastapi.Depends(
        backups_injectables.get_existing_pipeline
    ),
    db: orm.Session = fastapi.Depends(database.get_db),
) -> models.DatabasePipelineRun:
    if pipeline_run := crud.get_pipeline_run_by_id(db, pipeline_run_id):
        if pipeline_run.pipeline.id != pipeline.id:
            raise fastapi.HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "reason": f"The pipeline run with the ID {pipeline_run.id} does not belong to the pipeline with ID {pipeline.id}.",
                },
            )
        return pipeline_run
    raise fastapi.HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "reason": f"The pipeline run with the ID {pipeline_run_id} was not found.",
        },
    )
