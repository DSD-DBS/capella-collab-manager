# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import base64

import pytest
import responses
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.settings.modelsources.git.crud as git_crud
import capellacollab.settings.modelsources.git.models as git_models

# Example model badge
EXAMPLE_MODEL_BADGE = b"""
<svg
    xmlns="http://www.w3.org/2000/svg" width="536.0" height="120.0" viewBox="0 0 134 30">
    <g font-family="sans-serif" font-size="3.2">
        <rect fill="#FFF" stroke="#333" stroke-width="0.2" x="1" y="0" width="132" height="30" />
        <rect fill="#FFF" stroke="#333" stroke-width="0.2" x="23.8" y="1.4" width="108" height="22" />
        <g stroke="#555" stroke-width=".3">
            <path fill="#ffdd87" d="M3 5.5 h1.9 V7.4 h-2 z"/>
            <path fill="#a5c2e6" d="M3.8 6.4 h2 v1.8 h-2 z"/>
        </g>
        <text x="7" y="6.4">1274</text>
        <text x="7" y="9.4">objects</text>
        <g font-size="3.2">
            <rect fill="#ffdd87" stroke="#333" stroke-width="0" x="24.2" y="3.4" width="103.51020408163265" height="8" />
            <text x="25.2" y="8.4">100%</text>
            <rect fill="#91cc84" stroke="#333" stroke-width="0" x="127.71020408163265" y="3.4" width="0.163265306122449" height="8" />
            <rect fill="#a5c2e6" stroke="#333" stroke-width="0" x="127.87346938775511" y="3.4" width="0.163265306122449" height="8" />
            <rect fill="#f89f9f" stroke="#333" stroke-width="0" x="128.03673469387755" y="3.4" width="0.163265306122449" height="8" />
        </g>
        <g stroke="#555" stroke-width=".2">
            <path fill="#FFF" d="M2.5 15.200000000000001 h3.6 v3.1 H2.5 z"/>
            <path fill="#a5c2e6" d="M3 15.8 h1v.7 H3z m.8 1.2h1v.7h-1z m.9-1.1h.8v.6h-.8z"/>
            <path fill="none" d="M3.9 16.2 h.8 m-1.3.3.4.8 m1 .1.4-.9"/>
        </g>
        <text x="7" y="16.4">46</text>
        <text x="7" y="19.4">diagrams</text>
        <g font-size="3.2">
            <rect fill="#ffdd87" stroke="#333" stroke-width="0" x="24.2" y="13.4" width="104.0" height="8" />
            <text x="25.2" y="18.4">100%</text>
            <rect fill="#91cc84" stroke="#333" stroke-width="0" x="128.2" y="13.4" width="0.0" height="8" />
            <rect fill="#a5c2e6" stroke="#333" stroke-width="0" x="128.2" y="13.4" width="0.0" height="8" />
            <rect fill="#f89f9f" stroke="#333" stroke-width="0" x="128.2" y="13.4" width="0.0" height="8" />
        </g>
        <g font-size="2.8" fill="#555">
            <rect fill="#ffdd87" stroke="#333" stroke-width="0" x="3" y="25" width="5" height="3" />
            <text x="9" y="27.6">Operational Analysis</text>
            <rect fill="#91cc84" stroke="#333" stroke-width="0" x="37" y="25" width="5" height="3" />
            <text x="43" y="27.6">System Analysis</text>
            <rect fill="#a5c2e6" stroke="#333" stroke-width="0" x="67" y="25" width="5" height="3" />
            <text x="73" y="27.6">Logical Architecture</text>
            <rect fill="#f89f9f" stroke="#333" stroke-width="0" x="100" y="25" width="5" height="3" />
            <text x="106" y="27.6">Physical Architecture</text>
        </g>
    </g>
</svg>
"""


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
    responses.get(
        "https://example.com/api/v4/projects/test%2Fproject",
        status=200,
        json={"id": "10000"},
    )


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
    assert (
        response.json()["detail"]["err_code"] == "COMPLEXITY_BADGE_NOT_FOUND"
    )


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
