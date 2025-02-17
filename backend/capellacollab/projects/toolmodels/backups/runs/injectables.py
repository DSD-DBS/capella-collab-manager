# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0
import typing as t

import fastapi
from sqlalchemy import orm

from capellacollab.core import database
from capellacollab.projects.toolmodels.backups import (
    injectables as backups_injectables,
)
from capellacollab.projects.toolmodels.backups import models as backups_models

from . import crud, exceptions, models


def get_existing_pipeline_run(
    pipeline_run_id: int,
    pipeline: t.Annotated[
        backups_models.DatabaseBackup,
        fastapi.Depends(backups_injectables.get_existing_pipeline),
    ],
    db: t.Annotated[orm.Session, fastapi.Depends(database.get_db)],
) -> models.DatabasePipelineRun:
    if pipeline_run := crud.get_pipeline_run_by_id(db, pipeline_run_id):
        if pipeline_run.pipeline.id != pipeline.id:
            raise exceptions.PipelineRunBelongsToOtherPipelineError(
                pipeline_run_id=pipeline_run_id, pipeline_id=pipeline.id
            )
        return pipeline_run
    raise exceptions.PipelineRunNotFoundError(pipeline_run_id)
