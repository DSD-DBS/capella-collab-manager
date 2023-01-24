# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import random
import string

import pytest
import requests.exceptions
import sqlalchemy.exc
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.backups.crud as pipelines_crud
import capellacollab.projects.toolmodels.backups.models as pipelines_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.projects.toolmodels.modelsources.t4c.models as models_t4c_models
import capellacollab.sessions.operators
import capellacollab.settings.modelsources.t4c.models as t4c_models
import capellacollab.settings.modelsources.t4c.repositories.interface as t4c_repositories_interface
from capellacollab.core import credentials


@pytest.fixture(name="run_nightly", params=[True, False])
def fixture_run_nightly(
    request: pytest.FixtureRequest,
):
    return request.param


@pytest.fixture(name="include_commit_history", params=[True, False])
def fixture_include_commit_history(
    request: pytest.FixtureRequest,
):
    return request.param


@pytest.fixture(name="pipeline")
def fixture_pipeline(
    db: orm.Session,
    capella_model: toolmodels_models.CapellaModel,
    git_model: git_models.DatabaseGitModel,
    t4c_model: models_t4c_models.T4CModel,
    executor_name: str,
    run_nightly: bool,
    include_commit_history: bool,
) -> pipelines_models.DatabaseBackup:
    pipeline = pipelines_models.DatabaseBackup(
        k8s_cronjob_id="unavailable",
        git_model=git_model,
        t4c_model=t4c_model,
        created_by=executor_name,
        model=capella_model,
        t4c_username="no",
        t4c_password="no",
        include_commit_history=include_commit_history,
        run_nightly=run_nightly,
    )
    return pipelines_crud.create_pipeline(db, pipeline)


@pytest.fixture(name="mock_add_user_to_repository")
def fixture_mock_add_user_to_repository(monkeypatch: pytest.MonkeyPatch):
    def mock_add_user_to_repository(
        instance: t4c_models.DatabaseT4CInstance,
        repository_name: str,
        username: str,
        password: str = credentials.generate_password(),
        is_admin: bool = False,
    ):
        return {}

    monkeypatch.setattr(
        t4c_repositories_interface,
        "add_user_to_repository",
        mock_add_user_to_repository,
    )


class MockOperator:
    cronjob_counter = 0
    triggered_cronjob_counter = 0
    job_counter = 0

    def get_cronjob_last_run_by_label(self, label_key: str, label_value: str):
        return None

    def create_cronjob(
        self,
        image: str,
        environment: dict[str, str | None],
        schedule="* * * * *",
        timeout=18000,
    ) -> str:
        self.cronjob_counter += 1
        return self._generate_id()

    def trigger_cronjob(self, name: str, overwrite_environment=None) -> None:
        self.triggered_cronjob_counter += 1

    def create_job(
        self,
        image: str,
        labels: dict[str, str],
        environment: dict[str, str | None],
        timeout: int = 18000,
    ) -> str:
        self.job_counter += 1
        return self._generate_id()

    def _generate_id(self) -> str:
        return "".join(random.choices(string.ascii_lowercase, k=25))

    def delete_cronjob(self, _id: str):
        self.cronjob_counter -= 1
        return


@pytest.fixture(name="mockoperator")
def fixture_mockoperator(monkeypatch: pytest.MonkeyPatch):
    mockoperator = MockOperator()
    monkeypatch.setattr(
        capellacollab.sessions.operators, "OPERATOR", mockoperator
    )
    return mockoperator


@pytest.mark.usefixtures("project_manager", "mockoperator", "pipeline")
def test_get_all_pipelines_of_capellamodel(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    run_nightly: bool,
    include_commit_history: bool,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "k8s_cronjob_id": "unavailable",
            "lastrun": None,
            "t4c_model": {
                "project_name": "default",
                "repository_name": "test",
                "instance_name": "default",
            },
            "git_model": {
                "id": 1,
                "name": "",
                "path": "http://example.com",
                "entrypoint": "test/test.aird",
                "revision": "main",
                "primary": True,
                "username": "user",
                "password": True,
            },
            "run_nightly": run_nightly,
            "include_commit_history": include_commit_history,
        }
    ]


@pytest.mark.usefixtures(
    "project_manager",
    "mockoperator",
)
def test_create_pipeline_of_capellamodel_git_model_does_not_exist(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    t4c_model: models_t4c_models.T4CModel,
    client: testclient.TestClient,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines",
        json={
            "git_model_id": 0,
            "t4c_model_id": t4c_model.id,
            "include_commit_history": False,
            "run_nightly": False,
        },
    )

    assert response.status_code == 400
    assert {"err_code": "GIT_MODEL_NOT_EXISTANT"}.items() <= response.json()[
        "detail"
    ].items()


@pytest.mark.usefixtures(
    "project_manager", "mockoperator", "mock_add_user_to_repository"
)
def test_create_pipeline(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    t4c_model: models_t4c_models.T4CModel,
    git_model: git_models.GitModel,
    client: testclient.TestClient,
    run_nightly: bool,
    include_commit_history: bool,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines",
        json={
            "git_model_id": git_model.id,
            "t4c_model_id": t4c_model.id,
            "include_commit_history": include_commit_history,
            "run_nightly": run_nightly,
        },
    )

    assert response.status_code == 200
    assert {
        "id": 1,
        "lastrun": None,
        "t4c_model": {
            "project_name": "default",
            "repository_name": "test",
            "instance_name": "default",
        },
        "git_model": {
            "id": 1,
            "name": "",
            "path": "http://example.com",
            "entrypoint": "test/test.aird",
            "revision": "main",
            "primary": True,
            "username": "user",
            "password": True,
        },
        "run_nightly": run_nightly,
        "include_commit_history": include_commit_history,
    }.items() <= response.json().items()


@pytest.mark.usefixtures("project_manager", "mock_add_user_to_repository")
def test_trigger_pipeline(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
    run_nightly: bool,
    mockoperator: MockOperator,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs",
        json={
            "include_commit_history": "False",
        },
    )

    assert response.status_code == 201
    if run_nightly:
        assert mockoperator.triggered_cronjob_counter == 1
    else:
        assert mockoperator.job_counter == 1


@pytest.mark.usefixtures(
    "project_manager",
    "mockoperator",
)
def test_pipeline_creation_fails_if_t4c_server_not_available(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    t4c_model: models_t4c_models.T4CModel,
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
            "include_commit_history": False,
            "run_nightly": False,
        },
    )

    assert response.status_code == 503
    assert (
        response.json()["detail"]["err_code"]
        == "PIPELINE_CREATION_FAILED_T4C_SERVER_UNREACHABLE"
    )


@pytest.mark.usefixtures(
    "project_manager",
    "mockoperator",
)
def test_delete_pipeline(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    pipeline: pipelines_models.DatabaseBackup,
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
    mockoperator: MockOperator,
    run_nightly: bool,
):
    def mock_remove_user_from_repository(
        instance: t4c_models.DatabaseT4CInstance,
        repository_name: str,
        username: str,
    ):
        return

    monkeypatch.setattr(
        t4c_repositories_interface,
        "remove_user_from_repository",
        mock_remove_user_from_repository,
    )

    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}",
    )

    assert response.status_code == 204

    with pytest.raises(sqlalchemy.exc.NoResultFound):
        pipelines_crud.get_pipeline_by_id(db, pipeline.id)

    if run_nightly:
        assert mockoperator.cronjob_counter == -1


@pytest.mark.usefixtures(
    "project_manager",
    "mockoperator",
)
def test_pipeline_job_get_logs_no_last_run(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
    pipeline: pipelines_models.DatabaseBackup,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines/{pipeline.id}/runs/latest/logs",
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "PIPELINES_NO_LAST_RUN"
