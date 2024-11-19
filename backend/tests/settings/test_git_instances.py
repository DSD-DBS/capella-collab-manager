# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.git import crud as git_crud
from capellacollab.settings.modelsources.git import models as git_models


@pytest.fixture(name="git_instance")
def fixture_git_instance(db: orm.Session) -> git_models.DatabaseGitInstance:
    return git_crud.create_git_instance(
        db,
        git_models.PostGitInstance(
            name="test",
            url="https://example.com",
            type=git_models.GitType.GENERAL,
        ),
    )


@pytest.mark.usefixtures("admin", "git_instance")
def test_get_git_instances(client: testclient.TestClient):
    response = client.get("/api/v1/settings/modelsources/git")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert response.json()[-1]["name"] == "test"


@pytest.mark.usefixtures("admin")
def test_create_git_instance(db: orm.Session, client: testclient.TestClient):
    response = client.post(
        "/api/v1/settings/modelsources/git",
        json={
            "type": "General",
            "name": "example",
            "url": "https://example.com",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "example"

    assert git_crud.get_git_instance_by_id(db, response.json()["id"])


@pytest.mark.usefixtures("admin")
def test_get_git_instance(
    client: testclient.TestClient,
    git_instance: git_models.DatabaseGitInstance,
):
    response = client.get(
        f"/api/v1/settings/modelsources/git/{git_instance.id}",
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test"


@pytest.mark.usefixtures("admin")
def test_update_git_instance(
    db: orm.Session,
    client: testclient.TestClient,
    git_instance: git_models.DatabaseGitInstance,
):
    response = client.patch(
        f"/api/v1/settings/modelsources/git/{git_instance.id}",
        json={
            "type": "General",
            "name": "example2",
            "url": "https://example2.com",
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "example2"

    db_git_instance = git_crud.get_git_instance_by_id(
        db, response.json()["id"]
    )

    assert db_git_instance
    assert db_git_instance.name == "example2"


@pytest.mark.usefixtures("admin")
def test_delete_git_instance(
    db: orm.Session,
    client: testclient.TestClient,
    git_instance: git_models.DatabaseGitInstance,
):
    response = client.delete(
        f"/api/v1/settings/modelsources/git/{git_instance.id}",
    )
    assert response.status_code == 200

    assert not git_crud.get_git_instance_by_id(db, git_instance.id)


@pytest.mark.usefixtures("user", "mock_ls_remote")
def test_fetch_revisions(
    client: testclient.TestClient,
):

    response = client.post(
        "/api/v1/settings/modelsources/git/revisions",
        json={
            "url": "https://example.com/example.git",
            "credentials": {
                "username": "test",
                "password": "test",
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "branches": ["test-branch1", "test-branch2", "main"],
        "tags": ["v1.0.0", "v1.1.0"],
        "default": None,
    }


@pytest.mark.usefixtures("user", "git_instance")
def test_validate_path_valid(client: testclient.TestClient):
    response = client.post(
        "/api/v1/settings/modelsources/git/validate/path",
        json={
            "url": "https://example.com/example.git",
        },
    )
    assert response.json() is True


@pytest.mark.usefixtures("user")
def test_validate_path_without_git_instance(
    db: orm.Session, client: testclient.TestClient
):
    for instance in git_crud.get_git_instances(db):
        git_crud.delete_git_instance(db, git_instance=instance)
    response = client.post(
        "/api/v1/settings/modelsources/git/validate/path",
        json={
            "url": "https://example2.com/example.git",
        },
    )
    assert response.json() is True


@pytest.mark.usefixtures("user", "git_instance")
def test_validate_path_invalid(client: testclient.TestClient):
    response = client.post(
        "/api/v1/settings/modelsources/git/validate/path",
        json={
            "url": "https://example2.com/example.git",
        },
    )
    assert response.json() is False
