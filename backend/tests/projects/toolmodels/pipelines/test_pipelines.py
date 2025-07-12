# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
import requests.exceptions
import responses
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.backups.crud as pipelines_crud
import capellacollab.projects.toolmodels.backups.models as pipelines_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.projects.toolmodels.modelsources.t4c.models as models_t4c_models
import capellacollab.settings.modelsources.t4c.instance.models as t4c_models
import capellacollab.settings.modelsources.t4c.instance.repositories.interface as t4c_repositories_interface
from capellacollab.core import credentials


@pytest.mark.usefixtures("project_manager", "pipeline")
def test_get_all_pipelines_of_capellamodel(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.usefixtures("project_manager")
def test_get_pipeline_by_id(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabasePipeline,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == pipeline.id
    assert not response.json()["run_nightly"]
    assert response.json()["next_run"] is None


@pytest.mark.usefixtures("project_manager", "pipeline_scheduled", "scheduler")
def test_get_scheduled_pipeline_by_id(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabasePipeline,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == pipeline.id
    assert response.json()["run_nightly"]
    assert response.json()["next_run"] is not None


@pytest.mark.usefixtures("project_manager", "scheduler")
def test_update_pipeline(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabasePipeline,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}",
        json={"run_nightly": True},
    )

    assert response.status_code == 200
    assert response.json()["id"] == pipeline.id
    assert response.json()["run_nightly"]
    assert response.json()["next_run"] is not None

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}",
        json={"run_nightly": False},
    )

    assert response.status_code == 200
    assert response.json()["id"] == pipeline.id
    assert not response.json()["run_nightly"]
    assert response.json()["next_run"] is None


@pytest.mark.usefixtures(
    "project_manager",
)
def test_create_pipeline_of_capellamodel_git_model_does_not_exist(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    t4c_model: models_t4c_models.SimpleT4CModelWithRepository,
    client: testclient.TestClient,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines",
        json={
            "git_model_id": 0,
            "t4c_model_id": t4c_model.id,
            "run_nightly": False,
        },
    )

    assert response.status_code == 404
    assert {"err_code": "GIT_REPOSITORY_NOT_FOUND"}.items() <= response.json()[
        "detail"
    ].items()


@pytest.mark.usefixtures("project_manager", "mock_add_user_to_t4c_repository")
def test_create_pipeline(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    t4c_model: models_t4c_models.SimpleT4CModelWithRepository,
    git_model: git_models.GitModel,
    client: testclient.TestClient,
    run_nightly: bool,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines",
        json={
            "git_model_id": git_model.id,
            "t4c_model_id": t4c_model.id,
            "run_nightly": run_nightly,
        },
    )

    assert response.status_code == 200
    db_pipeline = pipelines_crud.get_pipeline_by_id(db, response.json()["id"])
    assert db_pipeline is not None
    assert db_pipeline.run_nightly == run_nightly


@pytest.mark.usefixtures(
    "project_manager",
)
def test_pipeline_creation_fails_if_t4c_server_not_available(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    t4c_model: models_t4c_models.SimpleT4CModelWithRepository,
    git_model: git_models.GitModel,
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    def mock_add_user_to_repository(
        instance: t4c_models.DatabaseT4CInstance,
        repository_name: str,
        username: str,
        password: str = credentials.generate_password(),
        is_admin: bool = False,
    ):
        raise requests.exceptions.ConnectionError()

    monkeypatch.setattr(
        t4c_repositories_interface,
        "add_user_to_repository",
        mock_add_user_to_repository,
    )

    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines",
        json={
            "git_model_id": git_model.id,
            "t4c_model_id": t4c_model.id,
            "run_nightly": False,
        },
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"]
        == "PIPELINE_OPERATION_FAILED_T4C_SERVER_UNREACHABLE"
    )


@responses.activate
@pytest.mark.usefixtures(
    "project_manager",
)
def test_delete_pipeline(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    client: testclient.TestClient,
    run_nightly: bool,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    responses.delete(
        f"{t4c_instance.rest_api}/users/{pipeline.t4c_username}?repositoryName={pipeline.t4c_model.repository.name}",
        json={},
        status=200,
    )

    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}",
    )

    assert response.status_code == 204

    assert not pipelines_crud.get_pipeline_by_id(db, pipeline.id)


@responses.activate
@pytest.mark.usefixtures(
    "project_manager",
)
def test_delete_pipeline_server_unreachable(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    client: testclient.TestClient,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    responses.delete(
        f"{t4c_instance.rest_api}/users/{pipeline.t4c_username}?repositoryName={pipeline.t4c_model.repository.name}",
        status=500,
    )

    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}",
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"]
        == "PIPELINE_OPERATION_FAILED_T4C_SERVER_UNREACHABLE"
    )


@responses.activate
@pytest.mark.usefixtures(
    "admin",
)
def test_delete_pipeline_server_unreachable_force(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    pipeline: pipelines_models.DatabasePipeline,
    client: testclient.TestClient,
    t4c_instance: t4c_models.DatabaseT4CInstance,
):
    responses.delete(
        f"{t4c_instance.rest_api}/users/{pipeline.t4c_username}?repositoryName={pipeline.t4c_model.repository.name}",
        status=500,
    )

    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}?force=True",
    )

    assert response.status_code == 204
    assert not pipelines_crud.get_pipeline_by_id(db, pipeline.id)
