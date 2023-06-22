# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import time

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.backups.models as pipelines_models
import capellacollab.projects.toolmodels.backups.runs.crud as pipeline_runs_crud
import capellacollab.projects.toolmodels.backups.runs.models as pipeline_runs_models
import capellacollab.projects.toolmodels.models as toolmodels_models
from capellacollab.core.logging import loki


@pytest.fixture(name="unix_time_in_ns")
def fixture_unix_time_in_ns() -> int:
    return time.time_ns()


@pytest.fixture(name="patch_loki")
def fixture_patch_loki(monkeypatch: pytest.MonkeyPatch, unix_time_in_ns: int):
    def fetch_logs_from_loki(
        query, start_time: datetime.datetime, end_time: datetime.datetime
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
    capella_model: toolmodels_models.CapellaModel,
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
    capella_model: toolmodels_models.CapellaModel,
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
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs",
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == pipeline_run.id


def test_get_pipeline_run(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
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
    capella_model: toolmodels_models.CapellaModel,
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
def def_get_logs(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    pipeline_run: pipeline_runs_models.DatabasePipelineRun,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/{pipeline_run.id}/logs",
    )

    assert response.status_code == 200
    assert b"test3" in response.content
