# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
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


class MockOperator:
    cronjob_counter = 0

    def create_cronjob(
        self,
        *args,
        **kwargs,
    ) -> str:
        self.cronjob_counter += 1
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
        capellacollab.sessions.operators, "get_operator", lambda: mockoperator
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
    assert len(response.json()) == 1


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

    assert response.status_code == 404
    assert {"err_code": "GIT_MODEL_NOT_EXISTING"}.items() <= response.json()[
        "detail"
    ].items()


@pytest.mark.usefixtures(
    "project_manager", "mockoperator", "mock_add_user_to_t4c_repository"
)
def test_create_pipeline(
    db: orm.Session,
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
    db_pipeline = pipelines_crud.get_pipeline_by_id(db, response.json()["id"])
    assert db_pipeline is not None
    assert db_pipeline.run_nightly == run_nightly
    assert db_pipeline.include_commit_history == include_commit_history


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

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"]
        == "PIPELINE_OPERATION_FAILED_T4C_SERVER_UNREACHABLE"
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

    assert not pipelines_crud.get_pipeline_by_id(db, pipeline.id)

    if run_nightly:
        assert mockoperator.cronjob_counter == -1
