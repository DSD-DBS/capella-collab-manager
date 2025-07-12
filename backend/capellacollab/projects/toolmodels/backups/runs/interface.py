# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging
import time

from kubernetes import client
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

POLL_INTERVAL = 5


def run_job_in_kubernetes(run_id: int):  # pragma: no cover
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


def _transform_kubernetes_logline_to_pydantic(
    line: str,
) -> models.PipelineLogLine:
    """Parse timestamp and log line from a Kubernetes log line."""
    try:
        timestamp = datetime.datetime.fromisoformat(line.split()[0])
    except Exception as e:
        log.warning(
            "Failed to parse timestamp from log line: '%s'. %s",
            line,
            e,
        )
        return models.PipelineLogLine(
            timestamp=datetime.datetime.now(datetime.UTC),
            text=line,
        )
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.UTC)
    return models.PipelineLogLine(
        timestamp=timestamp,
        text=line[31:],
    )


def _transform_kubernetes_event_to_pydantic(
    event: k8s_client.CoreV1Event,
) -> models.PipelineEvent:
    """Translate a Kubernetes event to logfmt format."""
    timestamp = (
        event.last_timestamp
        or event.event_time
        or datetime.datetime.now(datetime.UTC)
    )
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.UTC)
    return models.PipelineEvent(
        timestamp=timestamp, reason=event.reason, message=event.message
    )


def transform_event_to_logfmt(
    event: models.PipelineEvent,
) -> str:
    return f'reason="{event.reason}" message="{(event.message or "").replace('"', '\\"')}"'


def push_events(
    db: orm.Session,
    entries: list[models.PipelineEvent],
    run: models.DatabasePipelineRun,
):
    if loki.is_loki_activated():
        loki.push_logs_to_loki(
            entries=[
                loki.LogEntry(
                    timestamp=entry.timestamp,
                    line=transform_event_to_logfmt(entry),
                )
                for entry in entries
            ],
            labels={
                "job_name": run.reference_id or "",
                "pipeline_run_id": str(run.id),
                "log_type": pipeline_runs_models.LogType.EVENTS.value,
            },
        )
        return

    run.logs.extend(
        [
            models.DatabasePipelineRunLogLine(
                run=run,
                reason=entry.reason,
                line=entry.message or "",
                timestamp=entry.timestamp,
                log_type=pipeline_runs_models.LogType.EVENTS,
            )
            for entry in entries
        ]
    )
    db.commit()
    return


def push_logs(
    db: orm.Session,
    entries: list[models.PipelineLogLine],
    run: models.DatabasePipelineRun,
) -> None:
    if loki.is_loki_activated():
        log.info("Pushing logs to Loki for run %s", run.id)
        loki.push_logs_to_loki(
            entries=[
                loki.LogEntry(
                    timestamp=entry.timestamp,
                    line=entry.text,
                )
                for entry in entries
            ],
            labels={
                "job_name": run.reference_id or "",
                "pipeline_run_id": str(run.id),
                "log_type": pipeline_runs_models.LogType.LOGS.value,
            },
        )
        return

    log.info("Pushing logs to database for run %s", run.id)
    run.logs.extend(
        [
            models.DatabasePipelineRunLogLine(
                run=run,
                line=entry.text,
                timestamp=entry.timestamp,
                log_type=pipeline_runs_models.LogType.LOGS,
            )
            for entry in entries
        ]
    )
    db.commit()
    return


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
        return

    if events is None:
        log.info("No events found, skipping event collection")
        return

    event_entries = [
        _transform_kubernetes_event_to_pydantic(event) for event in events
    ]
    if run.events_last_fetched_timestamp:
        filtered_event_entries = [
            entry
            for entry in event_entries
            if entry.timestamp
            > run.events_last_fetched_timestamp.replace(tzinfo=datetime.UTC)
        ]
    else:
        filtered_event_entries = event_entries

    push_events(db, filtered_event_entries, run)

    if filtered_event_entries:
        run.events_last_fetched_timestamp = filtered_event_entries[
            -1
        ].timestamp
        db.commit()
    else:
        log.info("No new events found, skipping...")


def _fetch_logs_of_job_run(db: orm.Session, run: models.DatabasePipelineRun):
    """Fetch the logs of a job run since the last fetch time and report them to Loki."""

    if run.status in (
        models.PipelineRunStatus.PENDING,
        models.PipelineRunStatus.SCHEDULED,
    ):
        log.info(
            "Job %s is still pending, skipping log collection, status is %s",
            run.id,
            run.status,
        )
        return

    log.debug("Fetch logs of job %s", run.id)
    operator = operators.get_operator()
    try:
        logs = operator.get_job_logs(
            name=run.reference_id, since=run.logs_last_timestamp
        )
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
        _transform_kubernetes_logline_to_pydantic(log_line)
        for log_line in logs.splitlines()
    ]
    if run.logs_last_fetched_timestamp:
        filtered_log_entries = [
            entry
            for entry in log_entries
            if entry.timestamp
            > run.logs_last_fetched_timestamp.replace(tzinfo=datetime.UTC)
        ]
    else:
        filtered_log_entries = log_entries

    push_logs(db, filtered_log_entries, run)
    if filtered_log_entries:
        run.logs_last_timestamp = filtered_log_entries[-1].timestamp
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


def _get_pod_state(
    status: client.V1PodStatus,
) -> models.PipelineRunStatus:
    if not status.container_statuses:
        log.warning(
            "No container statuses found in pod status, setting status to UNKNOWN"
        )
        return models.PipelineRunStatus.UNKNOWN

    state: client.V1ContainerState = status.container_statuses[0].state

    if state.waiting:
        # https://github.com/kubernetes/kubernetes/blob/da215bf06a3b8ac3da4e0adb110dc5acc7f61fe1/pkg/kubelet/kubelet_pods.go#L83
        if state.waiting.reason in ("ContainerCreating", "PodInitializing"):
            return models.PipelineRunStatus.SCHEDULED

        # Handle errors like ImagePullBackOff properly
        return models.PipelineRunStatus.FAILURE

    return models.PipelineRunStatus.RUNNING


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
        pod = operators.get_operator().get_pod_for_job(
            job_name=job.metadata.name
        )
        return _get_pod_state(pod.status)
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
    pipelines_timeout = config.pipelines.timeout
    if run.trigger_time.replace(tzinfo=datetime.UTC) < datetime.datetime.now(
        datetime.UTC
    ) - datetime.timedelta(minutes=pipelines_timeout):
        log.info(
            "Job is not allowed to run longer than %d minutes, but was started at %s."
            " Updating status of pipeline %s to %s",
            pipelines_timeout,
            run.trigger_time,
            run.id,
            models.PipelineRunStatus.TIMEOUT.name,
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
            models.PipelineRunStatus.UNKNOWN.name,
        )
        run.status = models.PipelineRunStatus.UNKNOWN
        return

    target_status = _map_k8s_to_internal_status(job)

    if target_status != run.status:
        log.info(
            "Update status of pipeline %s from %s to %s",
            run.id,
            run.status.name,
            target_status.name,
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


def transform_loki_result_to_pipeline_event(
    loki_result: dict,
) -> models.PipelineEvent:
    """Parse timestamp and log line from a Kubernetes log line."""
    return models.PipelineEvent(
        timestamp=_transform_unix_nanoseconds_to_datetime(
            int(loki_result["values"][0][0])
        ),
        reason=loki_result["stream"]["reason"],
        message=loki_result["stream"]["message"],
    )


def transform_loki_result_to_pipeline_log(
    loki_value: dict,
) -> models.PipelineLogLine:
    """Parse timestamp and log line from a Kubernetes log line."""
    return models.PipelineLogLine(
        timestamp=_transform_unix_nanoseconds_to_datetime(int(loki_value[0])),
        text=loki_value[1],
    )


def _transform_unix_nanoseconds_to_datetime(
    nanoseconds: int,
) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(nanoseconds / 1e9, tz=datetime.UTC)
