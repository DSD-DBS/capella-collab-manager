# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import time
from unittest import mock

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.backups.models as pipelines_models
import capellacollab.projects.toolmodels.backups.runs.crud as pipeline_runs_crud
import capellacollab.projects.toolmodels.backups.runs.models as pipeline_runs_models
import capellacollab.projects.toolmodels.models as toolmodels_models
from capellacollab.__main__ import app
from capellacollab.configuration.app import config
from capellacollab.core.logging import loki
from capellacollab.projects.toolmodels.backups.runs import (
    injectables as runs_injectables,
)


@pytest.fixture(name="unix_time_in_ns")
def fixture_unix_time_in_ns() -> int:
    return time.time_ns()


@pytest.fixture(name="patch_loki")
def fixture_patch_loki(monkeypatch: pytest.MonkeyPatch, unix_time_in_ns: int):
    def fetch_logs_from_loki(
        query,
        start_time: datetime.datetime,
        end_time: datetime.datetime,
    ):
        return [
            {
                "values": [
                    [unix_time_in_ns, "test3"],
                    [unix_time_in_ns, "test2"],
                    [unix_time_in_ns, "test"],
                ],
            }
        ]

    monkeypatch.setattr(loki, "fetch_logs_from_loki", fetch_logs_from_loki)


@pytest.mark.usefixtures("project_manager")
def test_create_pipeline_run(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs",
        json={},
    )

    assert response.status_code == 200
    id = response.json()["id"]

    run = pipeline_runs_crud.get_pipeline_run_by_id(db, run_id=id)
    assert run.status == pipeline_runs_models.PipelineRunStatus.PENDING


@pytest.mark.usefixtures("project_manager")
def test_create_pipeline_run_with_custom_environment(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs",
        json={
            "include_commit_history": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["environment"] == {"INCLUDE_COMMIT_HISTORY": "true"}


def test_get_pipeline_runs(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs?page=1&size=50",
    )

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["id"] == pipeline_run.id


def test_get_pipeline_run(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == pipeline_run.id


@pytest.mark.usefixtures("patch_loki")
def test_get_events(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/events",
    )
    assert response.status_code == 200
    assert b"test3" in response.content


@pytest.mark.usefixtures("patch_loki")
def test_get_logs(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/logs",
    )

    assert response.status_code == 200
    assert b"test3" in response.content


@pytest.mark.parametrize(
    ("include_commit_history", "run_nightly"),
    [(False, False)],
)
def test_get_logs_with_loki_disabled(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(config.k8s.promtail, "loki_enabled", False)

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/logs",
    )

    assert response.status_code == 400
    assert response.json()["detail"]["err_code"] == "LOKI_DISABLED"


@pytest.fixture(name="mock_pipeline_run")
def fixture_mock_pipeline_run():
    mock_pipeline_run = mock.MagicMock(
        spec=pipeline_runs_models.DatabasePipelineRun
    )

    # Assign the values you want the mock object to return
    mock_pipeline_run.id = "mock_id"
    mock_pipeline_run.reference_id = "mock_reference_id"
    mock_pipeline_run.trigger_time = datetime.datetime.now(
        tz=datetime.UTC
    ) - datetime.timedelta(minutes=1)
    mock_pipeline_run.end_time = datetime.datetime.now(tz=datetime.UTC)

    # These values will be masked
    mock_pipeline_run.pipeline.t4c_password = "secret_pipeline_t4c_password"
    mock_pipeline_run.pipeline.t4c_model.repository.instance.password = (
        "secret_t4c_instance_password"
    )

    return mock_pipeline_run


@pytest.fixture(name="override_get_existing_pipeline_run_dependency")
def fixture_override_get_existing_pipeline_run_dependency(
    mock_pipeline_run: mock.Mock,
):
    def get_mock_existing_pipeline_run() -> (
        pipeline_runs_models.DatabasePipelineRun
    ):
        return mock_pipeline_run

    app.dependency_overrides[runs_injectables.get_existing_pipeline_run] = (
        get_mock_existing_pipeline_run
    )

    yield

    del app.dependency_overrides[runs_injectables.get_existing_pipeline_run]


@mock.patch("capellacollab.core.logging.loki.fetch_logs_from_loki")
@pytest.mark.usefixtures(
    "override_get_existing_pipeline_run_dependency", "admin"
)
def test_mask_logs(
    mock_fetch_logs: mock.Mock,
    client: testclient.TestClient,
):
    mock_fetch_logs.return_value = [
        {
            "values": [
                (
                    1618181583458797952,
                    "This is a log entry containing a secret_pipeline_t4c_password and secret_t4c_instance_password",
                )
            ]
        }
    ]

    response = client.get(
        "/api/v1/projects/1/models/1/backups/pipelines/1/runs/1/logs"
    )

    logs = response.json()

    assert "secret_pipeline_t4c_password" not in logs
    assert "secret_t4c_instance_password" not in logs
