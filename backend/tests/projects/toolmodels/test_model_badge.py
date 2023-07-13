# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import base64

import pytest
import responses
from aioresponses import aioresponses
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.settings.modelsources.git.crud as git_crud
import capellacollab.settings.modelsources.git.models as git_models

# Example model badge
EXAMPLE_MODEL_BADGE = b"<svg>badge placeholder</svg>"


@pytest.fixture(name="git_type", params=[git_models.GitType.GITLAB])
def fixture_git_type(request: pytest.FixtureRequest) -> git_models.GitType:
    return request.param


@pytest.fixture(
    name="git_instance_api_url", params=["https://example.com/api/v4"]
)
def fixture_git_instance_api_url(
    request: pytest.FixtureRequest,
) -> str:
    return request.param


@pytest.fixture(name="gitlab_instance")
def fixture_gitlab_instance(
    db: orm.Session, git_type: git_models.GitType, git_instance_api_url: str
) -> git_models.DatabaseGitInstance:
    git_instance = git_models.DatabaseGitInstance(
        name="test",
        url="https://example.com",
        api_url=git_instance_api_url,
        type=git_type,
    )
    return git_crud.create_git_instance(db, git_instance)


@pytest.fixture()
def mock_gitlab_rest_api():
    with aioresponses() as mocked:
        mocked.get(
            "https://example.com/api/v4/projects/test%2Fproject",
            status=200,
            payload={"id": "10000"},
        )
        yield mocked


@pytest.fixture
def mock_gitlab_model_badge_file_api():
    responses.get(
        "https://example.com/api/v4/projects/10000/repository/files/model-complexity-badge.svg?ref=main",
        status=200,
        json={
            "file_name": "model-complexity-badge.svg",
            "file_path": "model-complexity-badge.svg",
            "size": 2428,
            "encoding": "base64",
            "content_sha256": "ec00b56c2c87897dbd6e8d42de61b8ec6e3337cc442a09add86560920ec2872a",
            "ref": "main",
            "blob_id": "ee4b99b97f008dff549de9a40ddab139ea44435b",
            "commit_id": "1273b25fe671e014afb38d594825bb1a9d3206df",
            "last_commit_id": "85306aed4cf34c315ca3c31659fde02df9896e98",
            "execute_filemode": False,
            "content": base64.b64encode(EXAMPLE_MODEL_BADGE).decode(),
        },
    )


@pytest.fixture
def mock_gitlab_model_badge_file_api_not_found():
    responses.get(
        "https://example.com/api/v4/projects/10000/repository/files/model-complexity-badge.svg?ref=main",
        status=404,
    )


@responses.activate
@pytest.mark.parametrize(
    "git_type,git_instance_api_url",
    [(git_models.GitType.GENERAL, "https://example.com/api/v4")],
)
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
)
def test_get_model_badge_fails_without_gitlab_instance(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )

    assert response.status_code == 500
    assert (
        response.json()["detail"]["err_code"]
        == "INSTANCE_IS_NO_GITLAB_INSTANCE"
    )


@responses.activate
@pytest.mark.parametrize(
    "git_type,git_instance_api_url",
    [(git_models.GitType.GITLAB, "")],
)
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
)
def test_get_model_badge_fails_without_api_endpoint(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )

    assert response.status_code == 500
    assert (
        response.json()["detail"]["err_code"]
        == "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
    )


@responses.activate
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
    "mock_gitlab_model_badge_file_api_not_found",
)
def test_get_model_badge_not_found(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "FILE_NOT_FOUND"


@responses.activate
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
    "mock_gitlab_model_badge_file_api",
)
def test_get_model_badge(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_MODEL_BADGE
