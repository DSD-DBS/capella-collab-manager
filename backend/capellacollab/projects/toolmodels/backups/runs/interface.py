# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import datetime
import logging

from kubernetes import client as k8s_client
from kubernetes.client import exceptions as k8s_exceptions
from starlette import concurrency as starlette_concurrency

from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.core.logging import loki
from capellacollab.projects.toolmodels import (
    exceptions as toolmodels_exceptions,
)
from capellacollab.projects.toolmodels.backups import core as backups_core
from capellacollab.sessions import operators
from capellacollab.tools import crud as tools_crud

from .. import core as pipelines_core
from . import crud, models

log = logging.getLogger(__name__)

PIPELINES_TIMEOUT = config.pipelines.timeout


def schedule_refresh_and_trigger_pipeline_jobs(interval=5):
    async def loop():
        while True:
            try:
                await asyncio.sleep(interval)
                await starlette_concurrency.run_in_threadpool(
                    _refresh_and_trigger_pipeline_jobs
                )
            except asyncio.exceptions.CancelledError:
                return
            except BaseException:
                pass

    asyncio.ensure_future(loop())


def _schedule_pending_jobs():
    with database.SessionLocal() as db:
        for pending_run in crud.get_pipelines_runs_by_status(
            db, models.PipelineRunStatus.PENDING
        ):
            log.info(
                "Scheduling run for pipeline %s in project %s and model %s",
                pending_run.id,
                pending_run.pipeline.model.project.slug,
                pending_run.pipeline.model.slug,
            )
            try:
                model = pending_run.pipeline.model

                if not model.version_id:
                    raise toolmodels_exceptions.VersionIdNotSetError(model.id)

                job_name = operators.get_operator().create_job(
                    image=tools_crud.get_backup_image_for_tool_version(
                        db, model.version_id
                    ),
                    command="backup",
                    labels=pipelines_core.get_pipeline_labels(model)
                    | {
                        "app.capellacollab/pipelineID": str(
                            pending_run.pipeline.id
                        ),
                        "app.capellacollab/pipelineRunID": str(pending_run.id),
                    },
                    environment=pending_run.environment
                    | backups_core.get_environment(
                        pending_run.pipeline.git_model,
                        pending_run.pipeline.t4c_model,
                        pending_run.pipeline.t4c_username,
                        pending_run.pipeline.t4c_password,
                        pending_run.pipeline.include_commit_history,
                    ),
                    tool_resources=pending_run.pipeline.model.tool.config.resources.get_profile(
                        None
                    ),
                )
                pending_run.reference_id = job_name
                pending_run.status = models.PipelineRunStatus.SCHEDULED
            except Exception:
                log.error(
                    "Scheduling of job run with id %s failed", exc_info=True
                )
                pending_run.status = models.PipelineRunStatus.UNKNOWN
            db.commit()


def _transform_kubernetes_logline_to_loki_entry(
    line: str,
) -> loki.LogEntry:
    return loki.LogEntry(
        timestamp=datetime.datetime.fromisoformat(line.split()[0]),
        line=line[31:],
    )


def _transform_kubernetes_event_to_loki_entry(
    event: k8s_client.CoreV1Event,
) -> loki.LogEntry:
    timestamp = (
        event.last_timestamp
        or event.event_time
        or datetime.datetime.now(datetime.UTC)
    )
    return loki.LogEntry(
        timestamp=timestamp,
        line=f'reason="{event.reason}" message="{event.message}"',
    )


def _fetch_events_of_job_run(run: models.DatabasePipelineRun):
    log.debug("Fetch events of job %s", run.id)
    operator = operators.get_operator()
    try:
        events = operator.get_events_for_involved_object(name=run.reference_id)

        if pod := operator.get_pod_for_job(job_name=run.reference_id):
            events += operator.get_events_for_involved_object(
                pod.metadata.name
            )
    except Exception:
        log.exception(
            "Fetching events from Kubernetes cluster failed",
            extra={"run_id": run.id, "kubernetes_job_name": run.reference_id},
        )

    if events is None:
        log.debug("No events found, skipping event collection")
        return

    event_entries = [
        _transform_kubernetes_event_to_loki_entry(event) for event in events
    ]

    labels = {
        "job_name": run.reference_id or "",
        "pipeline_run_id": str(run.id),
        "log_type": "events",
    }

    try:
        loki.push_logs_to_loki(event_entries, labels)
    except Exception:
        log.exception("Failed pushing logs to loki", exc_info=True)
    run.logs_last_fetched_timestamp = datetime.datetime.now(datetime.UTC)


def _fetch_logs_of_job_runs(run: models.DatabasePipelineRun):
    log.debug("Fetch logs of job %s", run.id)
    operator = operators.get_operator()
    try:
        logs = operator.get_job_logs(name=run.reference_id)
    except Exception:
        log.exception(
            "Fetching logs from Kubernetes cluster failed",
            extra={"run_id": run.id, "kubernetes_job_name": run.reference_id},
        )
        return

    if logs is None:
        log.debug("No logs found, skipping log collection")
        return

    log_entries = [
        _transform_kubernetes_logline_to_loki_entry(log_line)
        for log_line in logs.splitlines()
    ]

    labels = {
        "job_name": run.reference_id or "",
        "pipeline_run_id": str(run.id),
        "log_type": "logs",
    }

    try:
        loki.push_logs_to_loki(log_entries, labels)
    except Exception:
        log.exception("Failed pushing logs to loki", exc_info=True)
    run.logs_last_fetched_timestamp = datetime.datetime.now(datetime.UTC)


def _terminate_job(run: models.DatabasePipelineRun):
    run.end_time = datetime.datetime.now(datetime.UTC)

    try:
        operators.get_operator().delete_job(name=run.reference_id)
    except Exception:
        log.exception(
            "Failed to delete job from Kubernetes cluster.",
            extra={
                "reference_id": run.reference_id,
                "run_id": run.id,
                "pipeline_id": run.pipeline.id,
                "model_slug": run.pipeline.model.slug,
                "project_slug": run.pipeline.model.project.slug,
            },
        )


def _map_k8s_to_internal_status(
    job: k8s_client.V1Job,
) -> models.PipelineRunStatus:
    conditions = job.status.conditions
    succeeded = job.status.succeeded
    failed = job.status.failed

    if conditions is not None:
        for condition in conditions:
            if (
                condition.reason == "DeadlineExceeded"
                and condition.status == "True"
            ):
                return models.PipelineRunStatus.TIMEOUT
    if succeeded and succeeded > 0:
        return models.PipelineRunStatus.SUCCESS
    elif failed and failed > 0:
        return models.PipelineRunStatus.FAILURE
    elif job.status.active:
        return models.PipelineRunStatus.RUNNING
    elif (
        job.status.active is None
        and (succeeded is None or succeeded == 0)
        and (failed is None or failed == 0)
    ):
        return models.PipelineRunStatus.SCHEDULED

    return models.PipelineRunStatus.UNKNOWN


def _update_status_of_job_run(
    run: models.DatabasePipelineRun,
):
    log.debug("Update status of pipeline", extra={"run_id": run.id})
    if run.trigger_time.replace(tzinfo=datetime.UTC) < datetime.datetime.now(
        datetime.UTC
    ) - datetime.timedelta(minutes=PIPELINES_TIMEOUT):
        run.status = models.PipelineRunStatus.TIMEOUT
        return

    try:
        job = operators.get_operator().get_job_by_name(run.reference_id)
    except k8s_exceptions.ApiException:
        log.exception(
            "Failed fetching the kubernetes job for pipeline run '%s'", run.id
        )
        run.status = models.PipelineRunStatus.UNKNOWN
        return

    current_status = _map_k8s_to_internal_status(job)

    if current_status != run.status:
        log.debug("Update status of pipeline %s to %s", run.id, run.status)
        run.status = current_status


def _job_is_finished(status: models.PipelineRunStatus):
    return status in (
        models.PipelineRunStatus.FAILURE,
        models.PipelineRunStatus.SUCCESS,
        models.PipelineRunStatus.UNKNOWN,
        models.PipelineRunStatus.TIMEOUT,
    )


def _refresh_and_trigger_pipeline_jobs():
    log.debug("Starting to refresh and trigger pipeline jobs...")
    _schedule_pending_jobs()
    with database.SessionLocal() as db:
        for run in crud.get_scheduled_or_running_pipelines(db):
            try:
                _update_status_of_job_run(run)
            except Exception:
                log.error(
                    "Failed updating the status of running and scheduled jobs",
                    exc_info=True,
                )

            try:
                _fetch_events_of_job_run(run)
            except Exception:
                log.error(
                    "Failed fetching events of jobs",
                    exc_info=True,
                )

            try:
                _fetch_logs_of_job_runs(run)
            except Exception:
                log.error(
                    "Failed fetching logs of jobs",
                    exc_info=True,
                )

            if _job_is_finished(run.status):
                _terminate_job(run)

            db.commit()
    log.debug("Finished refreshing and triggering of pipeline jobs.")
