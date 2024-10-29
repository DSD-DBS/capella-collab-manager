# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.settings.modelsources.git import core as git_core
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
    assert len(response.json()) == 2
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


@pytest.mark.usefixtures("user")
def test_fetch_revisions(
    monkeypatch: pytest.MonkeyPatch,
    client: testclient.TestClient,
):
    ls_remote = [
        "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847	HEAD",
        "e0f83d8d57ec1552c5fb76c83f7dff7f0ff86631	refs/heads/test-branch1",
        "76c71f5468f6e444317146c6c9a3e00033974a1c	refs/heads/test-branch2",
        "0665eb5bf5dc3a7bdcb30b4354c85eddde2bd847	refs/heads/main",
        "ea10a5a82f31807d89c1bb7fc61dcd331e49f8fc	refs/pull/100/head",
        "47cda65668eb258c5e84a8ffd43909ba4fac2661	refs/tags/v1.0.0",
        "bce139e467d3d60bd21a4097c78e86a87e1a5d21	refs/tags/v1.1.0",
    ]

    # pylint: disable=unused-argument
    def mock_ls_remote(*args, **kwargs):
        f: asyncio.Future = asyncio.Future()
        f.set_result(ls_remote)
        return f

    monkeypatch.setattr(git_core, "ls_remote", mock_ls_remote)

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
