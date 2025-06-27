# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from apscheduler import job as ap_job

from capellacollab import scheduling
from capellacollab.core import database
from capellacollab.projects.toolmodels.backups.runs import crud as runs_crud
from capellacollab.projects.toolmodels.backups.runs import (
    interface as runs_interface,
)
from capellacollab.projects.toolmodels.backups.runs import (
    models as runs_models,
)

from . import crud, models

logger = logging.getLogger(__name__)


def run_pipeline_in_kubernetes(pipeline_id: int) -> None:
    with database.SessionLocal() as db:
        pipeline = crud.get_pipeline_by_id(db, pipeline_id)
        if not pipeline:
            logger.error(
                "Pipeline with ID %d not found. Aborting pipeline triggering...",
                pipeline_id,
            )
            return
        run = runs_crud.create_pipeline_run(
            db,
            runs_models.DatabasePipelineRun(
                pipeline=pipeline,
                triggerer=None,
            ),
        )
        runs_interface.run_job_in_kubernetes(run.id)


def get_pipeline_scheduler(pipeline: models.Pipeline) -> ap_job.Job | None:
    job = scheduling.scheduler.get_job(f"pipeline-{pipeline.id}")
    if not job:
        logger.warning(
            "No scheduled job found for pipeline %d. If this error persists, recreate the pipeline.",
            pipeline.id,
        )
    return job
