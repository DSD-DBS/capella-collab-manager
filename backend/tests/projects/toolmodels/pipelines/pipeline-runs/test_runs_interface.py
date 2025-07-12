# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
from unittest import mock

import kubernetes
import pytest
from kubernetes import client as k8s_client
from kubernetes.client import exceptions as kubernetes_exceptions
from sqlalchemy import orm

from capellacollab.configuration.app import config
from capellacollab.projects.toolmodels.backups.runs import (
    interface as pipeline_runs_interface,
)
from capellacollab.projects.toolmodels.backups.runs import (
    models as pipeline_runs_models,
)


def test_job_scheduling(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a job is scheduled in the cluster."""
    create_namespaced_job = mock.Mock()
    monkeypatch.setattr(
        kubernetes.client.BatchV1Api,
        "create_namespaced_job",
        create_namespaced_job,
    )

    pipeline_runs_interface._schedule_job(db, pipeline_run)

    create_namespaced_job.assert_called_once()
    assert (
        pipeline_run.status == pipeline_runs_models.PipelineRunStatus.SCHEDULED
    )


def test_job_scheduling_without_version(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    caplog: pytest.LogCaptureFixture,
):
    """Test that a VersionIdNotSetError is raised if the model has no version."""
    pipeline_run.pipeline.model.version = None
    db.commit()

    pipeline_runs_interface._schedule_job(db, pipeline_run)

    assert "ERROR" in [record.levelname for record in caplog.records]
    assert (
        pipeline_run.status == pipeline_runs_models.PipelineRunStatus.UNKNOWN
    )


def test_job_scheduling_kube_error(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that a job status is changed to UNKNOWN if the scheduling fails."""

    create_namespaced_job = mock.Mock()
    create_namespaced_job.side_effect = kubernetes_exceptions.ApiException()

    monkeypatch.setattr(
        kubernetes.client.BatchV1Api,
        "create_namespaced_job",
        create_namespaced_job,
    )

    pipeline_runs_interface._schedule_job(db, pipeline_run)

    create_namespaced_job.assert_called_once()
    assert (
        pipeline_run.status == pipeline_runs_models.PipelineRunStatus.UNKNOWN
    )


@pytest.fixture(
    name="job_status",
)
def fixture_job_status(
    request: pytest.FixtureRequest,
) -> k8s_client.V1JobStatus:
    return request.param


@pytest.fixture(
    name="container_state",
)
def fixture_container_state(
    request: pytest.FixtureRequest,
) -> k8s_client.V1ContainerState | None:
    return request.param


@pytest.fixture(
    name="expected",
)
def fixture_expected(
    request: pytest.FixtureRequest,
) -> pipeline_runs_models.PipelineRunStatus:
    return request.param


@pytest.fixture(name="pod")
def fixture_pod(
    container_state: k8s_client.V1ContainerState | None,
    monkeypatch: pytest.MonkeyPatch,
) -> k8s_client.V1Pod | None:
    if not container_state:
        return None
    pod = k8s_client.V1Pod(
        metadata=k8s_client.V1ObjectMeta(
            name="example-pod",
            labels={
                "job-name": "example-job",
            },
        ),
        status=k8s_client.V1PodStatus(
            container_statuses=[
                k8s_client.V1ContainerStatus(
                    name="pipeline-run",
                    state=container_state,
                    image="hello-world",
                    image_id="hello-world",
                    ready=True,
                    restart_count=0,
                ),
            ],
        ),
    )

    monkeypatch.setattr(
        k8s_client.CoreV1Api,
        "read_namespaced_pod",
        lambda *args, **kwargs: pod,
    )

    monkeypatch.setattr(
        k8s_client.CoreV1Api,
        "list_namespaced_pod",
        lambda *args, **kwargs: k8s_client.V1PodList(items=[pod]),
    )

    return pod


@pytest.fixture(name="job")
def fixture_job(
    job_status: k8s_client.V1JobStatus,
    monkeypatch: pytest.MonkeyPatch,
) -> k8s_client.V1JobStatus:
    job = k8s_client.V1Job(
        metadata=k8s_client.V1ObjectMeta(name="example-job"),
        status=job_status,
    )

    monkeypatch.setattr(
        k8s_client.BatchV1Api,
        "read_namespaced_job",
        lambda *args, **kwargs: job,
    )


@pytest.mark.parametrize(
    ("job_status", "container_state", "expected"),
    [
        (
            k8s_client.V1JobStatus(
                conditions=[
                    k8s_client.V1JobCondition(
                        reason="DeadlineExceeded", status="True", type="Failed"
                    )
                ],
                succeeded=0,
                failed=1,
                active=None,
            ),
            None,
            pipeline_runs_models.PipelineRunStatus.TIMEOUT,
        ),
        (
            k8s_client.V1JobStatus(
                conditions=None, succeeded=1, failed=0, active=None
            ),
            None,
            pipeline_runs_models.PipelineRunStatus.SUCCESS,
        ),
        (
            k8s_client.V1JobStatus(
                conditions=None, succeeded=0, failed=1, active=None
            ),
            None,
            pipeline_runs_models.PipelineRunStatus.FAILURE,
        ),
        (
            k8s_client.V1JobStatus(
                conditions=None, succeeded=0, failed=0, active=True
            ),
            k8s_client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=k8s_client.V1ContainerStateWaiting(
                    reason="PodInitializing"
                ),
            ),
            pipeline_runs_models.PipelineRunStatus.SCHEDULED,
        ),
        (
            k8s_client.V1JobStatus(
                conditions=None, succeeded=0, failed=0, active=True
            ),
            k8s_client.V1ContainerState(
                running=None,
                terminated=None,
                waiting=k8s_client.V1ContainerStateWaiting(
                    reason="ImagePullBackOff"
                ),
            ),
            pipeline_runs_models.PipelineRunStatus.FAILURE,
        ),
        (
            k8s_client.V1JobStatus(
                conditions=None, succeeded=0, failed=0, active=True
            ),
            k8s_client.V1ContainerState(
                running=k8s_client.V1ContainerStateRunning(),
                terminated=None,
                waiting=None,
            ),
            pipeline_runs_models.PipelineRunStatus.RUNNING,
        ),
        (
            k8s_client.V1JobStatus(
                conditions=None, succeeded=0, failed=0, active=None
            ),
            None,
            pipeline_runs_models.PipelineRunStatus.SCHEDULED,
        ),
    ],
)
@pytest.mark.usefixtures("pod", "job")
def test_get_job_state(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    expected: pipeline_runs_models.PipelineRunStatus,
):
    """Test that a running container is mapped to the expected state."""

    pipeline_runs_interface._update_status_of_job_run(db, pipeline_run)
    assert pipeline_run.status == expected


def test_get_job_state_timeout(
    db: orm.Session,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    freeze_time: datetime.datetime,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that an exceeded deadline is mapped to TIMEOUT"""
    monkeypatch.setattr(config.pipelines, "timeout", 90)
    pipeline_run.trigger_time = freeze_time - datetime.timedelta(hours=2)
    pipeline_runs_interface._update_status_of_job_run(db, pipeline_run)
    assert (
        pipeline_run.status == pipeline_runs_models.PipelineRunStatus.TIMEOUT
    )
