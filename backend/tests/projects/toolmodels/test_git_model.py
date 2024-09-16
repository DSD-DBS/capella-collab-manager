# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.crud as project_git_crud
import capellacollab.projects.toolmodels.modelsources.git.models as project_git_models


@pytest.mark.usefixtures("git_instance", "project_manager", "capella_model")
def test_reset_repository_id_on_git_model_path_change(
    db: orm.Session,
    git_model: project_git_models.DatabaseGitModel,
    client: testclient.TestClient,
):
    assert git_model.repository_id is None

    project_git_crud.update_git_model_repository_id(db, git_model, "1")

    assert git_model.repository_id == "1"

    new_path = "https://example.com/test/project/anything"
    response = client.put(
        f"/api/v1/projects/{git_model.model.project.slug}/models/{git_model.model.slug}/modelsources/git/{git_model.id}",
        json={
            "path": new_path,
            "entrypoint": git_model.entrypoint,
            "revision": git_model.revision,
            "username": git_model.username,
            "password": "",
            "primary": git_model.primary,
        },
    )

    assert response.status_code == 200

    assert git_model.repository_id is None
    assert git_model.path == new_path

    assert response.json()["repository_id"] is None
    assert response.json()["path"] == new_path


@pytest.mark.usefixtures("project_manager", "capella_model")
def test_delete_git_model(
    git_model: project_git_models.DatabaseGitModel,
    client: testclient.TestClient,
):
    project_slug = git_model.model.project.slug
    model_slug = git_model.model.slug

    del_response = client.delete(
        f"/api/v1/projects/{project_slug}/models/{model_slug}/modelsources/git/{git_model.id}"
    )

    assert del_response.status_code == 204

    get_response = client.get(
        f"/api/v1/projects/{project_slug}/models/{model_slug}/modelsources/git"
    )

    assert get_response.status_code == 200
    assert len(get_response.json()) == 0


@pytest.mark.usefixtures("git_instance", "project_manager", "capella_model")
def test_raise_instance_prefix_unmatched_error_on_model_update(
    git_model: project_git_models.DatabaseGitModel,
    client: testclient.TestClient,
):
    response = client.put(
        f"/api/v1/projects/{git_model.model.project.slug}/models/{git_model.model.slug}/modelsources/git/{git_model.id}",
        json={
            "path": "https://unknown.com/test/project",
            "entrypoint": git_model.entrypoint,
            "revision": git_model.revision,
            "username": git_model.username,
            "password": "",
            "primary": git_model.primary,
        },
    )

    assert response.status_code == 404
    assert (
        response.json()["detail"]["err_code"]
        == "NO_GIT_INSTANCE_WITH_PREFIX_FOUND"
    )
