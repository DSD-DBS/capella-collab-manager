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


class MockOperator:
    def get_cronjob_last_run_by_label(self, label_key: str, label_value: str):
        return None


@pytest.mark.usefixtures("project_manager")
def test_get_all_pipelines_of_capellamodel(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    pipeline: pipelines_models.DatabaseBackup,
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        capellacollab.sessions.operators, "OPERATOR", MockOperator()
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/backups/pipelines"
    )

    assert response.status_code == 200
    assert response.json() == []
