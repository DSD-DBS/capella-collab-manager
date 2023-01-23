# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.backups.crud as pipelines_crud
import capellacollab.projects.toolmodels.backups.models as pipelines_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.projects.toolmodels.modelsources.t4c.models as models_t4c_models
import capellacollab.sessions.operators


@pytest.fixture(name="pipeline")
def fixture_pipeline(
    db: orm.Session,
    capella_model: toolmodels_models.CapellaModel,
    git_model: git_models.DatabaseGitModel,
    t4c_model: models_t4c_models.T4CModel,
    executor_name: str,
) -> pipelines_models.DatabaseBackup:
    pipeline = pipelines_models.DatabaseBackup(
        k8s_cronjob_id="unavailable",
        git_model=git_model,
        t4c_model=t4c_model,
        created_by=executor_name,
        model=capella_model,
        t4c_username="no",
        t4c_password="no",
        include_commit_history=False,
        run_nightly=False,
    )
    return pipelines_crud.create_pipeline(db, pipeline)


@pytest.fixture(name="mockoperator")
def fixture_mockoperator(monkeypatch: pytest.MonkeyPatch):
    class MockOperator:
        def get_cronjob_last_run_by_label(
            self, label_key: str, label_value: str
        ):
            return None

    monkeypatch.setattr(
        capellacollab.sessions.operators, "OPERATOR", MockOperator()
    )


@pytest.mark.usefixtures("project_manager", "mockoperator", "pipeline")
def test_get_all_pipelines_of_capellamodel(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
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
            "run_nightly": False,
            "include_commit_history": False,
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
