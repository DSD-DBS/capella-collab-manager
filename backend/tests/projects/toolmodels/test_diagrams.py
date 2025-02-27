# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import io
import json
import zipfile

import aioresponses
import pytest
from fastapi import testclient

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.models as projects_git_models
import capellacollab.settings.modelsources.git.models as git_models
from capellacollab.projects.toolmodels.diagrams import core as diagrams_core
from tests.projects.toolmodels.modelsources.handler import (
    mocks as git_handler_mocks,
)

EXAMPLE_SVG = b"""
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   xmlns="http://www.w3.org/2000/svg"
   xmlns:svg="http://www.w3.org/2000/svg">
    <rect
       style="fill:#000000;stroke-width:0.264583"
       width="100"
       height="30"
    />
</svg>
"""


def get_diagram_cache_index():
    return [
        {
            "name": "Diagram 1",
            "uuid": "_c90e4Hdf2d2UosmJBo0GTw",
            "success": "true",
        },
        {
            "name": "Diagram 2",
            "uuid": "_VjvUMasdf2e2wVuAPh3ezQ",
            "success": "true",
        },
    ]


def get_zipfile():
    byte_io = io.BytesIO()
    with zipfile.ZipFile(byte_io, "w") as zf:
        zf.writestr(
            "index.json", str(get_diagram_cache_index()).replace("'", '"')
        )
        zf.writestr("_c90e4Hdf2d2UosmJBo0GTw.svg", EXAMPLE_SVG)
    byte_io.seek(0)
    return byte_io.read()


@pytest.fixture(name="mock_git_diagram_cache_index_api")
def fixture_mock_git_diagram_cache_index_api(
    git_type: git_models.GitType, aiomock: aioresponses.aioresponses
):
    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/diagram_cache/index.json",
                status=200,
                payload=get_diagram_cache_index(),
            )
        case git_models.GitType.GITHUB:
            aiomock.get(
                "https://example.com/api/v4/repos/test/project/actions/artifacts/12347/zip",
                status=200,
                body=get_zipfile(),
                content_type="application/zip",
            )


def mock_git_diagram_cache_from_repo_api(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    status_code: int = 200,
):
    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/10000/repository/files/diagram_cache%2Findex.json?ref=diagram-cache%2Fmain",
                status=status_code,
                payload={
                    "file_name": "index.json",
                    "file_path": "diagram_cache/index.json",
                    "content": base64.b64encode(
                        json.dumps(get_diagram_cache_index()).encode("utf-8")
                    ).decode(),
                },
            )
            aiomock.get(
                "https://example.com/api/v4/projects/10000/repository/files/diagram_cache%2F_c90e4Hdf2d2UosmJBo0GTw.svg?ref=diagram-cache%2Fmain",
                status=status_code,
                payload={
                    "file_name": "_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "file_path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "content": base64.b64encode(EXAMPLE_SVG).decode(),
                },
            )
        case git_models.GitType.GITHUB:
            aiomock.get(
                "https://example.com/api/v4/repos/test/project/contents/diagram_cache/index.json?ref=diagram-cache%252Fmain",
                status=status_code,
                repeat=True,
                payload={
                    "name": "index.json",
                    "path": "diagram_cache/index.json",
                    "content": base64.b64encode(
                        json.dumps(get_diagram_cache_index()).encode("utf-8")
                    ).decode(),
                },
            )
            aiomock.get(
                "https://example.com/api/v4/repos/test/project/contents/diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg?ref=diagram-cache%252Fmain",
                status=status_code,
                repeat=True,
                payload={
                    "name": "_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "content": base64.b64encode(EXAMPLE_SVG).decode(),
                },
            )


@pytest.fixture(name="mock_fetch_diagram_cache_metadata")
def fixture_mock_fetch_diagram_cache_metadata(monkeypatch: pytest.MonkeyPatch):
    async def mock_fetch_diagram_cache_metadata(logger, handler, job_id):
        return (
            None,
            None,
            json.dumps(get_diagram_cache_index()),
        )

    monkeypatch.setattr(
        diagrams_core,
        "fetch_diagram_cache_metadata",
        mock_fetch_diagram_cache_metadata,
    )


@pytest.fixture(name="mock_git_diagram_cache_svg")
def fixture_mock_git_diagram_cache_svg(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
):
    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                status=200,
                body=EXAMPLE_SVG,
            )
        case git_models.GitType.GITHUB:
            # fixture mock_git_diagram_cache_index_api already provides all that is needed
            pass


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_valkey_cache",
    "mock_git_diagram_cache_index_api",
)
def test_get_diagram_metadata_from_repository(
    git_type: git_models.GitType,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    aiomock: aioresponses.aioresponses,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock)
    git_handler_mocks.mock_git_get_commit_information_api(
        git_type=git_type,
        aiomock=aiomock,
        path="diagram_cache/index.json",
        revision="diagram-cache/main",
    )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        ["12345", "12346"],
        aiomock,
    )
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_valkey_cache",
    "mock_git_diagram_cache_index_api",
)
def test_get_diagram_metadata_from_artifacts(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock, 404)
    git_handler_mocks.mock_git_get_commit_information_api(
        git_type=git_type,
        aiomock=aiomock,
        path="diagram_cache/index.json",
        revision="diagram-cache/main",
    )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        ["12345", "12346"],
        aiomock,
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.parametrize(
    "git_type",
    [git_models.GitType.GENERAL],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
)
def test_get_diagrams_fails_without_git_instance(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 400
    assert response.json()["detail"]["err_code"] == "GIT_INSTANCE_UNSUPPORTED"


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
)
def test_get_diagrams_fails_without_api_endpoint(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    git_instance: git_models.DatabaseGitInstance,
):
    git_instance.api_url = ""
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"]
        == "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
    )


@pytest.mark.usefixtures(
    "project_user", "git_instance", "git_model", "mock_git_valkey_cache"
)
def test_get_diagram_cache_without_defined_job(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock, 404)
    git_handler_mocks.mock_git_get_commit_information_api(
        git_type=git_type,
        aiomock=aiomock,
        path="diagram_cache/index.json",
        revision="diagram-cache/main",
    )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        [],
        aiomock,
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "PIPELINE_JOB_NOT_FOUND"


@pytest.mark.usefixtures(
    "project_user", "git_instance", "git_model", "mock_git_valkey_cache"
)
def test_get_diagrams_failed_diagram_cache_job_found(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock, 404)
    git_handler_mocks.mock_git_get_commit_information_api(
        git_type=git_type,
        aiomock=aiomock,
        path="diagram_cache/index.json",
        revision="diagram-cache/main",
    )

    job_status = "failed"
    if git_type == git_models.GitType.GITHUB:
        job_status = "failure"

    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        job_status,
        ["12345", "12346"],
        aiomock,
    )
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    reason = response.json()["detail"]["reason"]
    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"] == "UNSUCCESSFUL_JOB_STATE_ERROR"
    )
    assert "failure" in reason or "failed" in reason


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_valkey_cache",
    "mock_fetch_diagram_cache_metadata",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
)
def test_get_single_diagram_from_artifacts(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock, 404)
    for filename in ("index.json", "_c90e4Hdf2d2UosmJBo0GTw.svg"):
        git_handler_mocks.mock_git_get_commit_information_api(
            git_type=git_type,
            aiomock=aiomock,
            path=f"diagram_cache/{filename}",
            revision="diagram-cache/main",
        )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        ["12345", "12346"],
        aiomock,
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_valkey_cache",
    "mock_fetch_diagram_cache_metadata",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
)
def test_get_single_diagram_from_artifacts_with_file_ending(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock, 404)
    for filename in ("index.json", "_c90e4Hdf2d2UosmJBo0GTw.svg"):
        git_handler_mocks.mock_git_get_commit_information_api(
            git_type=git_type,
            aiomock=aiomock,
            path=f"diagram_cache/{filename}",
            revision="diagram-cache/main",
        )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        ["12345", "12346"],
        aiomock,
    )
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw.svg",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
)
def test_get_single_diagram_from_artifacts_with_wrong_file_ending(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock, 404)
    for filename in ("index.json", "_c90e4Hdf2d2UosmJBo0GTw.svg"):
        git_handler_mocks.mock_git_get_commit_information_api(
            git_type=git_type,
            aiomock=aiomock,
            path=f"diagram_cache/{filename}",
            revision="diagram-cache/main",
        )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        ["12345", "12346"],
        aiomock,
    )
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw.png",
    )

    assert response.status_code == 400


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_fetch_diagram_cache_metadata",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
)
def test_get_single_diagram_from_file_and_cache(
    git_type: git_models.GitType,
    aiomock: aioresponses.aioresponses,
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    mock_git_valkey_cache,
):
    mock_git_diagram_cache_from_repo_api(git_type, aiomock)
    for filename in ("index.json", "_c90e4Hdf2d2UosmJBo0GTw.svg"):
        git_handler_mocks.mock_git_get_commit_information_api(
            git_type=git_type,
            aiomock=aiomock,
            path=f"diagram_cache/{filename}",
            revision="diagram-cache/main",
        )
    git_handler_mocks.mock_git_rest_api_for_artifacts(
        git_type,
        "update_capella_diagram_cache",
        "success",
        ["12345", "12346"],
        aiomock,
    )

    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG

    client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw"
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG

    assert len(mock_git_valkey_cache.cache) == 1


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
)
def test_diagram_not_found_in_cache(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
    git_model: projects_git_models.DatabaseGitModel,
):
    git_model.repository_id = "10000"

    async def mock_fetch_diagram_cache_metadata(logger, handler, job_id):
        return None, None, json.dumps([])

    monkeypatch.setattr(
        diagrams_core,
        "fetch_diagram_cache_metadata",
        mock_fetch_diagram_cache_metadata,
    )
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_invalid-diagram",
    )
    assert response.status_code == 404
    assert (
        response.json()["detail"]["err_code"]
        == "DIAGRAM_CACHE_DIAGRAM_NOT_FOUND"
    )


@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
)
def test_diagram_unsuccessful(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    monkeypatch: pytest.MonkeyPatch,
    git_model: projects_git_models.DatabaseGitModel,
):
    git_model.repository_id = "10000"

    async def mock_fetch_diagram_cache_metadata(logger, handler, job_id):
        return (
            None,
            None,
            json.dumps(
                [
                    {
                        "name": "Diagram 1",
                        "uuid": "_c90e4Hdf2d2UosmJBo0GTw",
                        "success": False,
                    }
                ]
            ),
        )

    monkeypatch.setattr(
        diagrams_core,
        "fetch_diagram_cache_metadata",
        mock_fetch_diagram_cache_metadata,
    )
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw",
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "DIAGRAM_CACHE_DIAGRAM_NOT_SUCCESSFUL"
    )
