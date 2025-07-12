# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import logging

from apscheduler import job as ap_job
from apscheduler.schedulers import base as ap_base
from apscheduler.triggers import cron as ap_cron_trigger
from sqlalchemy import orm

from capellacollab import scheduling
from capellacollab.configuration import core as configuration_core
from capellacollab.configuration import models as configuration_models
from capellacollab.core import database
from capellacollab.projects.toolmodels.backups.runs import crud as runs_crud
from capellacollab.projects.toolmodels.backups.runs import (
    interface as pipeline_runs_interface,
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
        pipeline_runs_interface.run_job_in_kubernetes(run.id)


def get_scheduled_pipeline_job(pipeline: models.Pipeline) -> ap_job.Job | None:
    job = scheduling.scheduler.get_job(f"pipeline-{pipeline.id}")
    if not job:
        logger.warning(
            "No scheduled job found for pipeline %d. If this error persists, recreate the pipeline.",
            pipeline.id,
        )
    return job


def schedule_pipeline(
    db: orm.Session, pipeline: models.DatabasePipeline
) -> ap_job.Job:
    pipeline_config = configuration_core.get_global_configuration(db).pipelines

    return scheduling.scheduler.add_job(
        run_pipeline_in_kubernetes,
        trigger=ap_cron_trigger.CronTrigger.from_crontab(
            pipeline_config.cron, timezone=pipeline_config.timezone
        ),
        args=[pipeline.id],
        id=f"pipeline-{pipeline.id}",
        name=f"Pipeline {pipeline.id}",
        coalesce=True,
        misfire_grace_time=pipeline_config.misfire_grace_time,
    )


def unschedule_pipeline(pipeline: models.DatabasePipeline) -> None:
    try:
        scheduling.scheduler.remove_job(f"pipeline-{pipeline.id}")
    except ap_base.JobLookupError as e:
        logger.warning(
            "Job for pipeline %s not found during deletion: %s",
            pipeline.id,
            e,
        )


def update_trigger_configuration(
    configuration: configuration_models.PipelineConfiguration,
):
    """Update the trigger configuration for all pipelines."""
    jobs: list[ap_job.Job] = [
        job
        for job in scheduling.scheduler.get_jobs()
        if job.id.startswith("pipeline-")
    ]

    logger.info(
        "Updating trigger configuration for %d pipelines to '%s', timezone %s and misfire_grace_time %s",
        len(jobs),
        configuration.cron,
        configuration.timezone,
        configuration.misfire_grace_time,
    )

    for job in jobs:
        job.modify(
            misfire_grace_time=configuration.misfire_grace_time,
        )
        job.reschedule(
            trigger=ap_cron_trigger.CronTrigger.from_crontab(
                configuration.cron, timezone=configuration.timezone
            ),
        )

    logger.info(
        "The updated schedule for scheduled jobs is: %s",
        ", ".join(
            [
                f"{job.name} {job.trigger!r}"
                for job in scheduling.scheduler.get_jobs()
            ]
        ),
    )
