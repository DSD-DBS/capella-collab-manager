# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient

import capellacollab.projects.models as projects_models
from capellacollab.projects.volumes import models as projects_volumes_models
from capellacollab.sessions.operators import k8s


@pytest.mark.usefixtures("user", "project_user")
def test_get_project_volume(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    project_volume: projects_volumes_models.DatabaseProjectVolume,
):
    """Test getting the project volume of a project"""
    response = client.get(f"/api/v1/projects/{project.slug}/volumes")
    assert response.status_code == 200
    assert response.json()["id"] == project_volume.id
    assert response.json()["size"] == "2Gi"


@pytest.mark.usefixtures("user", "project_user")
def test_get_project_volume_not_found(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
):
    """Test getting the project volume of a project if it doesn't exist"""
    response = client.get(f"/api/v1/projects/{project.slug}/volumes")
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.usefixtures("user", "project_manager")
def test_get_individual_project_volume(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    project_volume: projects_volumes_models.DatabaseProjectVolume,
):
    """Test getting a project volume by ID of a project"""
    response = client.get(
        f"/api/v1/projects/{project.slug}/volumes/{project_volume.id}"
    )
    assert response.status_code == 200
    assert response.json()["id"] == project_volume.id
    assert response.json()["size"] == "2Gi"


@pytest.mark.usefixtures("user", "project_user")
def test_get_individual_project_volume_not_found(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
):
    """Test getting a project volume by ID of a project if it doesn't exist"""
    response = client.get(f"/api/v1/projects/{project.slug}/volumes/1")
    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "PROJECT_VOLUME_NOT_FOUND"


@pytest.mark.usefixtures("user", "project_manager")
def test_create_project_volume(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test creating a project volume"""
    mock_create_persistent_volume_count = 0

    def mock_create_persistent_volume(
        self, name: str, size: str, labels: dict
    ):
        nonlocal mock_create_persistent_volume_count
        mock_create_persistent_volume_count += 1

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "create_persistent_volume",
        mock_create_persistent_volume,
    )

    response = client.post(f"/api/v1/projects/{project.slug}/volumes")

    assert response.status_code == 200
    assert mock_create_persistent_volume_count == 1


@pytest.mark.usefixtures("user", "project_volume", "project_manager")
def test_create_project_volume_already_exists(
    client: testclient.TestClient, project: projects_models.DatabaseProject
):
    """Test creating a project volume in a project where already one exists"""
    response = client.post(f"/api/v1/projects/{project.slug}/volumes")

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"] == "ONLY_ONE_VOLUME_PER_PROJECT"
    )


@pytest.mark.usefixtures("user", "project_manager")
def test_delete_project_volume(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    project_volume: projects_volumes_models.DatabaseProjectVolume,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test deleting a project volume"""

    delete_persistent_volume_count = 0

    def mock_delete_persistent_volume(self, name: str):
        nonlocal delete_persistent_volume_count
        delete_persistent_volume_count += 1

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "delete_persistent_volume",
        mock_delete_persistent_volume,
    )

    response = client.delete(
        f"/api/v1/projects/{project.slug}/volumes/{project_volume.id}"
    )
    assert response.status_code == 204
