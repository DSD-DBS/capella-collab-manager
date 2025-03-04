# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import io
import zipfile

import aioresponses
import pytest
from fastapi import testclient

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.settings.modelsources.git.models as git_models
from tests.projects.toolmodels.modelsources.handler import (
    mocks as git_handler_mocks,
)

# Example model badge
EXAMPLE_MODEL_BADGE = b"<svg>badge placeholder</svg>"


@pytest.fixture(name="mock_git_rest_api")
def fixture_mock_git_rest_api(
    git_type: git_models.GitType, aiomock: aioresponses.aioresponses
):
    match git_type:
        case git_models.GitType.GITHUB:
            aiomock.get("https://api.example.com/", status=200)
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/test%2Fproject",
                status=200,
                payload={"id": "10000"},
            )


def mock_git_model_badge_file_api(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    status_code: int = 200,
):
    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/10000/repository/files/model-complexity-badge.svg?ref=main",
                status=status_code,
                payload={
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
        case git_models.GitType.GITHUB:
            aiomock.get(
                "https://example.com/api/v4/repos/test/project/contents/model-complexity-badge.svg?ref=main",
                status=status_code,
                repeat=True,
                payload={
                    "name": "model-complexity-badge.svg",
                    "path": "model-complexity-badge.svg",
                    "size": 2428,
                    "encoding": "base64",
                    "sha": "528b30485e043489df3e103e6cfb2f6d16f84cf5",
                    "content": base64.b64encode(EXAMPLE_MODEL_BADGE).decode(),
                },
            )


def get_zipfile():
    byte_io = io.BytesIO()
    with zipfile.ZipFile(byte_io, "w") as zf:
        zf.writestr("model-complexity-badge.svg", EXAMPLE_MODEL_BADGE)
    byte_io.seek(0)
    return byte_io.read()


@pytest.mark.usefixtures("project_user", "git_type", "git_model")
def test_model_has_no_git_instance(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )
    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "NO_MATCHING_GIT_INSTANCE"


@pytest.mark.parametrize(
    ("git_type"),
    [(git_models.GitType.GENERAL)],
)
@pytest.mark.usefixtures("project_user", "git_instance", "git_model")
def test_get_model_badge_fails_with_unsupported_git_instance(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )
    assert response.status_code == 400
    assert response.json()["detail"]["err_code"] == "GIT_INSTANCE_UNSUPPORTED"


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
)
def test_get_model_badge_fails_without_api_endpoint(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    git_instance: git_models.DatabaseGitInstance,
    client: testclient.TestClient,
):
    git_instance.api_url = ""
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )
    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"]
        == "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
    )


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_valkey_cache",
    "mock_git_rest_api",
)
def test_get_model_badge(
    git_type: git_models.GitType,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    aiomock: aioresponses.aioresponses,
):
    git_handler_mocks.mock_git_get_commit_information_api(
        git_type=git_type,
        aiomock=aiomock,
        path="model-complexity-badge.svg",
    )
    mock_git_model_badge_file_api(git_type, aiomock)
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "generate-model-badge",
        "success",
        ["12345", "12346"],
        aiomock,
    )
    mock_get_model_badge_from_artifacts_api(git_type, aiomock)
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_MODEL_BADGE


def mock_get_model_badge_from_artifacts_api(
    git_type: git_models.GitType, aiomock: aioresponses.aioresponses
):
    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/model-complexity-badge.svg",
                status=200,
                body=EXAMPLE_MODEL_BADGE,
            )
        case git_models.GitType.GITHUB:
            aiomock.get(
                "https://example.com/api/v4/repos/test/project/actions/artifacts/12347/zip",
                status=200,
                body=get_zipfile(),
                content_type="application/zip",
            )


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_valkey_cache",
    "mock_git_rest_api",
)
def test_get_model_badge_from_artifacts(
    git_type: git_models.GitType,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    aiomock: aioresponses.aioresponses,
):
    git_handler_mocks.mock_git_get_commit_information_api(
        git_type=git_type,
        aiomock=aiomock,
        path="model-complexity-badge.svg",
    )
    mock_git_model_badge_file_api(git_type, aiomock, status_code=404)
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "generate-model-badge",
        "success",
        ["12345", "12346"],
        aiomock,
    )
    mock_get_model_badge_from_artifacts_api(git_type, aiomock)

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/badges/complexity",
    )
    assert response.status_code == 200
    assert response.content == EXAMPLE_MODEL_BADGE
