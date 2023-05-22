# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import datetime
import logging

import kubernetes.client
import kubernetes.client.exceptions
import pytz
from sqlalchemy import orm
from starlette.concurrency import run_in_threadpool

from capellacollab.core import database
from capellacollab.core.logging import loki
from capellacollab.projects.toolmodels.backups import core as backups_core
from capellacollab.sessions import operators
from capellacollab.tools import crud as tools_crud

from . import crud, models

log = logging.getLogger(__name__)


async def schedule_refresh_and_trigger_pipeline_jobs(interval=5):
    async def loop():
        while True:
            try:
                await asyncio.sleep(interval)
                await run_in_threadpool(refresh_and_trigger_pipeline_jobs)
            except asyncio.exceptions.CancelledError:
                return
            except BaseException:
                pass

    asyncio.ensure_future(loop())


def schedule_pending_jobs():
    log.debug(
        "Scheduling jobs for pipelines in kubernetes cluster",
    )
    with database.SessionLocal() as db:
        for pending_run in crud.get_all_pipelines_runs_by_status(
            db, models.PipelineRunStatus.PENDING
        ):
            log.info(
                "Scheduling run for pipeline %s in project %s and model %s",
                pending_run.id,
                pending_run.pipeline.model.project.slug,
                pending_run.pipeline.model.slug,
            )
            try:
                job_name = operators.get_operator().create_job(
                    image=tools_crud.get_backup_image_for_tool_version(
                        db, pending_run.pipeline.model.version_id
                    ),
                    labels={
                        "app.capellacollab/projectSlug": pending_run.pipeline.model.project.slug,
                        "app.capellacollab/projectID": str(
                            pending_run.pipeline.model.project.id
                        ),
                        "app.capellacollab/modelSlug": pending_run.pipeline.model.slug,
                        "app.capellacollab/modelID": str(
                            pending_run.pipeline.model.id
                        ),
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
                    ),
                )
                pending_run.reference_id = job_name
                pending_run.status = models.PipelineRunStatus.SCHEDULED
            except:  # pylint: disable=bare-except
                log.error(
                    "Scheduling of job run with id %s failed", exc_info=True
                )
                pending_run.status = models.PipelineRunStatus.UNKNOWN
            db.commit()


def transform_kubernetes_logline_to_loki_entry(line: str):
    datetime_without_nanoseconds = line.split()[0][:-11]
    timestamp = datetime.datetime.strptime(
        datetime_without_nanoseconds, "%Y-%m-%dT%H:%M:%S"
    )

    # Transform UTC from kubernetes to local timezone
    timestamp = timestamp.replace(tzinfo=pytz.UTC).astimezone()
    return {"timestamp": timestamp, "line": " ".join(line.split()[1:])}


def transform_kubernetes_event_to_loki_entry(
    event: kubernetes.client.CoreV1Event,
) -> dict[str, str]:
    # Transform UTC from kubernetes to local timezone
    timestamp = (
        event.last_timestamp.replace(tzinfo=pytz.UTC).astimezone()
        if event.last_timestamp
        else datetime.datetime.now()
    )
    return {
        "timestamp": timestamp,
        "line": f'reason="{event.reason}" message="{event.message}"',
    }


def fetch_events_of_jobs(run: models.DatabasePipelineRun):
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

    event_entries = []
    for line in events:
        event_entries.append(transform_kubernetes_event_to_loki_entry(line))

    labels = {
        "job_name": run.reference_id,
        "pipeline_run_id": run.id,
        "log_type": "events",
    }

    try:
        loki.push_logs_to_loki(event_entries, labels)
    except Exception:
        log.exception("Failed pushing logs to loki", exc_info=True)
    run.logs_last_fetched_timestamp = datetime.datetime.now().astimezone()


def fetch_logs_of_jobs(run: models.DatabasePipelineRun):
    log.debug("Fetch logs of job %s", run.id)
    operator = operators.get_operator()
    try:
        logs = operator.get_job_logs(
            name=run.reference_id,
        )
    except Exception:
        log.exception(
            "Fetching logs from Kubernetes cluster failed",
            extra={"run_id": run.id, "kubernetes_job_name": run.reference_id},
        )
        return

    if logs is None:
        log.debug("No logs found, skipping log collection")
        return

    log_entries = []
    for line in logs.splitlines():
        log_entries.append(transform_kubernetes_logline_to_loki_entry(line))

    labels = {
        "job_name": run.reference_id,
        "pipeline_run_id": run.id,
        "log_type": "logs",
    }

    try:
        loki.push_logs_to_loki(log_entries, labels)
    except Exception:
        log.exception("Failed pushing logs to loki", exc_info=True)
    run.logs_last_fetched_timestamp = datetime.datetime.now().astimezone()


def timeout_jobs(db: orm.Session, run: models.DatabasePipelineRun):
    if (
        run.trigger_time.astimezone()
        < datetime.datetime.now().astimezone() - datetime.timedelta(minutes=60)
    ):
        log.info("Timing out job with ID %s", run.id)
        run.status = models.PipelineRunStatus.TIMEOUT
        db.commit()
        try:
            operators.get_operator().delete_job(name=run.reference_id)
        except Exception:
            log.error("Failed to delete timed out job.")


def map_k8s_status_to_internal(
    job: kubernetes.client.V1Job,
) -> models.PipelineRunStatus:
    conditions = job.status.conditions
    succeeded = job.status.succeeded
    failed = job.status.failed

    if conditions is not None:
        for condition in conditions:
            # Check for timeouts
            if (
                condition.reason == "DeadlineExceeded"
                and condition.status == "True"
            ):
                return models.PipelineRunStatus.TIMEOUT
    # Check for success
    if succeeded and succeeded > 0:
        return models.PipelineRunStatus.SUCCESS
    # Check for failure (e.g., container failure)
    elif failed and failed > 0:
        return models.PipelineRunStatus.FAILURE
    # Running state
    elif job.status.active:
        return models.PipelineRunStatus.RUNNING
    # Scheduled state
    elif (
        job.status.active is None
        and (succeeded is None or succeeded == 0)
        and (failed is None or failed == 0)
    ):
        return models.PipelineRunStatus.SCHEDULED
    # Unknown state
    else:
        return models.PipelineRunStatus.UNKNOWN


def update_status_of_running_and_scheduled_jobs(
    run: models.DatabasePipelineRun,
):
    log.debug("Update status of pipeline", extra={"run_id": run.id})
    try:
        job = operators.get_operator().get_job_by_name(run.reference_id)
    except kubernetes.client.exceptions.ApiException:
        log.exception(
            "Failed fetching the kubernetes job for pipeline run '%s'", run.id
        )
        run.status = models.PipelineRunStatus.UNKNOWN
        return
    new_status = map_k8s_status_to_internal(job)
    if new_status != run.status:
        log.debug("Update status of pipeline %s to %s", run.id, run.status)
        run.status = new_status


def reap_unknown_jobs_in_cluster(db: orm.Session):
    log.debug("Searching for unknown jobs in cluster to reap")
    active_pipeline_references = {
        run.reference_id
        for run in crud.get_scheduled_and_running_pipelines(db)
    }
    job_names = {
        job.metadata.name for job in operators.get_operator().get_jobs()
    }
    for job_name in job_names - active_pipeline_references:
        log.warning("Reap unknown job '%s'", job_name)
        operators.get_operator().delete_job(job_name)


def refresh_and_trigger_pipeline_jobs():
    schedule_pending_jobs()
    with database.SessionLocal() as db:
        reap_unknown_jobs_in_cluster(db)
        for run in crud.get_scheduled_and_running_pipelines(db):
            try:
                timeout_jobs(db, run)
            except:  # pylint: disable=bare-except
                log.error("Failed timeout of jobs", exc_info=True)

            try:
                update_status_of_running_and_scheduled_jobs(run)
                db.commit()
            except:  # pylint: disable=bare-except
                log.error(
                    "Failed updating the status of running and scheduled jobs",
                    exc_info=True,
                )

            try:
                fetch_events_of_jobs(run)
            except:  # pylint: disable=bare-except
                log.error(
                    "Failed fetching events of jobs",
                    exc_info=True,
                )

            try:
                fetch_logs_of_jobs(run)
            except:  # pylint: disable=bare-except
                log.error(
                    "Failed fetching logs of jobs",
                    exc_info=True,
                )
            db.commit()
