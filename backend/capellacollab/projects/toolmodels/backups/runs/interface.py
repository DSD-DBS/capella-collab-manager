# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import time

from kubernetes import client as k8s_client
from kubernetes.client import exceptions as k8s_exceptions
from sqlalchemy import orm

from capellacollab.configuration.app import config
from capellacollab.core import database
from capellacollab.core.logging import loki
from capellacollab.projects.toolmodels import (
    exceptions as toolmodels_exceptions,
)
from capellacollab.projects.toolmodels.backups import core as backups_core
from capellacollab.projects.toolmodels.backups.runs import (
    models as pipeline_runs_models,
)
from capellacollab.sessions import operators
from capellacollab.tools import crud as tools_crud

from .. import core as pipelines_core
from . import crud, models

log = logging.getLogger(__name__)

PIPELINES_TIMEOUT = config.pipelines.timeout
POLL_INTERVAL = 5


def run_job_in_kubernetes(run_id: int):
    """Run a job in the Kubernetes cluster and wait until completion."""

    with database.SessionLocal() as db:
        run = crud.get_pipeline_run_by_id(db, run_id)
        assert run is not None
        _schedule_job(db, run)
        while True:
            time.sleep(POLL_INTERVAL)
            _update_status_of_job_run(db, run)
            _fetch_events_of_job_run(db, run)
            _fetch_logs_of_job_run(db, run)
            if _job_is_finished(run.status):
                _terminate_job(run)
                break


def _schedule_job(db: orm.Session, run: models.DatabasePipelineRun):
    """Schedule a job run in the Kubernetes cluster.

    The function updates to run status to SCHEDULED or UNKNOWN.
    After job creation, the Kubernetes job name is stored as "reference_id"
    """

    log.info(
        "Scheduling run for pipeline run %s in project %s and model %s",
        run.id,
        run.pipeline.model.project.slug,
        run.pipeline.model.slug,
    )
    try:
        model = run.pipeline.model

        if not model.version_id:
            raise toolmodels_exceptions.VersionIdNotSetError(model.id)

        job_name = operators.get_operator().create_job(
            image=tools_crud.get_backup_image_for_tool_version(
                db, model.version_id
            ),
            command="backup",
            labels=pipelines_core.get_pipeline_labels(model)
            | {
                "app.capellacollab/pipelineID": str(run.pipeline.id),
                "app.capellacollab/pipelineRunID": str(run.id),
            },
            environment=run.environment
            | backups_core.get_environment(
                run.pipeline.git_model,
                run.pipeline.t4c_model,
                run.pipeline.t4c_username,
                run.pipeline.t4c_password,
                run.pipeline.include_commit_history,
            ),
            tool_resources=run.pipeline.model.tool.config.resources,
        )
        run.reference_id = job_name
        log.info(
            "Scheduled job for pipeline run %s as '%s' in the cluster.",
            run.id,
            job_name,
        )
        run.status = models.PipelineRunStatus.SCHEDULED
    except Exception:
        log.exception("Scheduling of job run with id %s failed", run.id)
        run.status = models.PipelineRunStatus.UNKNOWN
    db.commit()


def _transform_kubernetes_logline_to_loki_entry(
    line: str,
) -> loki.LogEntry:
    """Parse timestamp and log line from a Kubernetes log line."""
    timestamp = datetime.datetime.fromisoformat(line.split()[0])
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.UTC)
    return loki.LogEntry(
        timestamp=timestamp,
        line=line[31:],
    )


def _transform_kubernetes_event_to_loki_entry(
    event: k8s_client.CoreV1Event,
) -> loki.LogEntry:
    """Translate a Kubernetes event to logfmt format."""
    timestamp = (
        event.last_timestamp
        or event.event_time
        or datetime.datetime.now(datetime.UTC)
    )
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.UTC)
    return loki.LogEntry(
        timestamp=timestamp,
        line=f'reason="{event.reason}" message="{event.message}"',
    )


def push_logs(
    db: orm.Session,
    entries: list[loki.LogEntry],
    run: models.DatabasePipelineRun,
    log_type: pipeline_runs_models.LogType,
) -> None:
    labels = {
        "job_name": run.reference_id or "",
        "pipeline_run_id": str(run.id),
        "log_type": log_type.value,
    }

    if not loki.is_loki_activated():
        run.logs.extend(
            [
                models.DatabasePipelineRunLogLine(
                    run=run,
                    line=entry["line"],
                    timestamp=entry["timestamp"],
                    log_type=log_type,
                )
                for entry in entries
            ]
        )
        db.commit()
        return

    try:
        loki.push_logs_to_loki(entries, labels)
    except Exception:
        log.exception("Failed pushing logs to loki")


def _fetch_events_of_job_run(db: orm.Session, run: models.DatabasePipelineRun):
    """Fetch the events of a job run and report them to Loki."""
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
        log.info("No events found, skipping event collection")
        return

    event_entries = [
        _transform_kubernetes_event_to_loki_entry(event) for event in events
    ]
    if run.events_last_fetched_timestamp:
        filtered_event_entries = [
            entry
            for entry in event_entries
            if entry["timestamp"]
            > run.events_last_fetched_timestamp.replace(tzinfo=datetime.UTC)
        ]
    else:
        filtered_event_entries = event_entries

    push_logs(
        db, filtered_event_entries, run, pipeline_runs_models.LogType.EVENTS
    )

    if filtered_event_entries:
        run.events_last_fetched_timestamp = filtered_event_entries[-1][
            "timestamp"
        ]
        db.commit()
    else:
        log.info("No new events found, skipping...")


def _fetch_logs_of_job_run(db: orm.Session, run: models.DatabasePipelineRun):
    """Fetch the logs of a job run since the last fetch time and report them to Loki."""

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
        log.info("No logs found, skipping log collection")
        return

    log_entries = [
        _transform_kubernetes_logline_to_loki_entry(log_line)
        for log_line in logs.splitlines()
    ]
    if run.logs_last_fetched_timestamp:
        filtered_log_entries = [
            entry
            for entry in log_entries
            if entry["timestamp"]
            > run.logs_last_fetched_timestamp.replace(tzinfo=datetime.UTC)
        ]
    else:
        filtered_log_entries = log_entries

    push_logs(db, filtered_log_entries, run, pipeline_runs_models.LogType.LOGS)
    if filtered_log_entries:
        run.logs_last_timestamp = filtered_log_entries[-1]["timestamp"]
    else:
        log.info("No new logs found, skipping...")
    run.logs_last_fetched_timestamp = datetime.datetime.now(datetime.UTC)
    db.commit()


def _terminate_job(run: models.DatabasePipelineRun):
    """Terminate a job run in the Kubernetes cluster."""

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
    """Map the Kubernetes job status to our internal status model."""

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
    if failed and failed > 0:
        return models.PipelineRunStatus.FAILURE
    if job.status.active:
        return models.PipelineRunStatus.RUNNING
    if (
        job.status.active is None
        and (succeeded is None or succeeded == 0)
        and (failed is None or failed == 0)
    ):
        return models.PipelineRunStatus.SCHEDULED

    return models.PipelineRunStatus.UNKNOWN


def _update_status_of_job_run(
    db: orm.Session, run: models.DatabasePipelineRun
):
    """Update the internal status of a job run based on the Kubernetes job status or timeout."""
    if run.trigger_time.replace(tzinfo=datetime.UTC) < datetime.datetime.now(
        datetime.UTC
    ) - datetime.timedelta(minutes=PIPELINES_TIMEOUT):
        log.info(
            "Update status of pipeline %s to %s",
            run.id,
            models.PipelineRunStatus.TIMEOUT,
        )
        run.status = models.PipelineRunStatus.TIMEOUT
        return

    try:
        job = operators.get_operator().get_job_by_name(run.reference_id)
    except k8s_exceptions.ApiException:
        log.exception(
            "Failed fetching the kubernetes job for pipeline run '%s'", run.id
        )
        log.info(
            "Update status of pipeline %s to %s",
            run.id,
            models.PipelineRunStatus.UNKNOWN,
        )
        run.status = models.PipelineRunStatus.UNKNOWN
        return

    target_status = _map_k8s_to_internal_status(job)

    if target_status != run.status:
        log.info(
            "Update status of pipeline %s from %s to %s",
            run.id,
            run.status,
            target_status,
        )
        run.status = target_status

    db.commit()


def _job_is_finished(status: models.PipelineRunStatus):
    return status in (
        models.PipelineRunStatus.FAILURE,
        models.PipelineRunStatus.SUCCESS,
        models.PipelineRunStatus.UNKNOWN,
        models.PipelineRunStatus.TIMEOUT,
    )
