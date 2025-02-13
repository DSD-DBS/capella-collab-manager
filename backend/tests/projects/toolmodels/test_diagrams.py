# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import io
import json
import zipfile

import pytest
import responses
from fastapi import testclient

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.settings.modelsources.git.models as git_models

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
def fixture_mock_git_diagram_cache_index_api(git_type: git_models.GitType):
    match git_type:
        case git_models.GitType.GITLAB:
            responses.get(
                "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/diagram_cache/index.json",
                status=200,
                json=get_diagram_cache_index(),
            )
        case git_models.GitType.GITHUB:
            responses.get(
                "https://example.com/api/v4/repos/test/project/actions/artifacts/12347/zip",
                status=200,
                body=get_zipfile(),
                content_type="application/zip",
            )


@pytest.fixture(name="mock_git_diagram_cache_from_repo_api")
def fixture_mock_git_diagram_cache_from_repo_api(
    git_type: git_models.GitType, git_response_status: int
):
    match git_type:
        case git_models.GitType.GITLAB:
            responses.get(
                "https://example.com/api/v4/projects/10000/repository/files/diagram_cache%2Findex.json?ref=diagram-cache%2Fmain",
                status=git_response_status,
                json={
                    "file_name": "index.json",
                    "file_path": "diagram_cache/index.json",
                    "content": base64.b64encode(
                        json.dumps(get_diagram_cache_index()).encode("utf-8")
                    ).decode(),
                },
            )
            responses.get(
                "https://example.com/api/v4/projects/10000/repository/files/diagram_cache%2F_c90e4Hdf2d2UosmJBo0GTw.svg?ref=diagram-cache%2Fmain",
                status=git_response_status,
                json={
                    "file_name": "_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "file_path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "content": base64.b64encode(EXAMPLE_SVG).decode(),
                },
            )
        case git_models.GitType.GITHUB:
            responses.get(
                "https://example.com/api/v4/repos/test/project/contents/diagram_cache/index.json?ref=diagram-cache%2Fmain",
                status=git_response_status,
                json={
                    "name": "index.json",
                    "path": "diagram_cache/index.json",
                    "content": base64.b64encode(
                        json.dumps(get_diagram_cache_index()).encode("utf-8")
                    ).decode(),
                },
            )
            responses.get(
                "https://example.com/api/v4/repos/test/project/contents/diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg?ref=diagram-cache%2Fmain",
                status=git_response_status,
                json={
                    "name": "_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "content": base64.b64encode(EXAMPLE_SVG).decode(),
                },
            )


@pytest.fixture(name="mock_git_diagram_cache_svg")
def fixture_mock_gitlab_diagram_cache_svg(git_type: git_models.GitType):
    match git_type:
        case git_models.GitType.GITLAB:
            responses.get(
                "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                status=200,
                body=EXAMPLE_SVG,
            )
        case git_models.GitType.GITHUB:
            # fixture mock_git_diagram_cache_index_api already provides all that is needed
            pass


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                }
            ],
        ),
        (
            git_models.GitType.GITHUB,
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                }
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_get_commit_information_api",
    "mock_git_valkey_cache",
)
def test_get_diagram_metadata_from_repository(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_response_status", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                }
            ],
        ),
        (
            git_models.GitType.GITHUB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                }
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_get_commit_information_api",
    "mock_git_valkey_cache",
)
def test_get_diagram_metadata_from_artifacts(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    assert response.status_code == 200
    assert len(response.json()) == 3


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_instance_api_url"),
    [(git_models.GitType.GENERAL, "https://example.com/api/v4")],
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


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_instance_api_url"),
    [(git_models.GitType.GITLAB, ""), (git_models.GitType.GITHUB, "")],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
)
def test_get_diagrams_fails_without_api_endpoint(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 422
    assert (
        response.json()["detail"]["err_code"]
        == "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
    )


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_response_status", "pipeline_ids", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            404,
            [],
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                }
            ],
        ),
        (
            git_models.GitType.GITHUB,
            404,
            [],
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                }
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_get_commit_information_api",
)
def test_get_diagram_cache_without_defined_job(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "PIPELINE_JOB_NOT_FOUND"


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_response_status", "job_status", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            404,
            "failed",
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                }
            ],
        ),
        (
            git_models.GitType.GITHUB,
            404,
            "failure",
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                }
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_get_commit_information_api",
)
def test_get_diagrams_failed_diagram_cache_job_found(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    reason = response.json()["detail"]["reason"]
    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"] == "UNSUCCESSFUL_JOB_STATE_ERROR"
    )
    assert "failure" in reason or "failed" in reason


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_response_status", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "ref_name": "diagram-cache/main",
                },
            ],
        ),
        (
            git_models.GitType.GITHUB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "sha": "diagram-cache/main",
                },
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
    "mock_git_get_commit_information_api",
    "mock_git_valkey_cache",
)
def test_get_single_diagram_from_artifacts(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_response_status", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "ref_name": "diagram-cache/main",
                },
            ],
        ),
        (
            git_models.GitType.GITHUB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "sha": "diagram-cache/main",
                },
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
    "mock_git_get_commit_information_api",
    "mock_git_valkey_cache",
)
def test_get_single_diagram_from_artifacts_with_file_ending(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw.svg",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_response_status", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "ref_name": "diagram-cache/main",
                },
            ],
        ),
        (
            git_models.GitType.GITHUB,
            404,
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "sha": "diagram-cache/main",
                },
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
    "mock_git_get_commit_information_api",
)
def test_get_single_diagram_from_artifacts_with_wrong_file_ending(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw.png",
    )

    assert response.status_code == 400


@responses.activate
@pytest.mark.parametrize(
    ("git_type", "git_query_params"),
    [
        (
            git_models.GitType.GITLAB,
            [
                {
                    "path": "diagram_cache/index.json",
                    "ref_name": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "ref_name": "diagram-cache/main",
                },
            ],
        ),
        (
            git_models.GitType.GITHUB,
            [
                {
                    "path": "diagram_cache/index.json",
                    "sha": "diagram-cache/main",
                },
                {
                    "path": "diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
                    "sha": "diagram-cache/main",
                },
            ],
        ),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_diagram_cache_from_repo_api",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
    "mock_git_get_commit_information_api",
    "mock_git_valkey_cache",
)
def test_get_single_diagram_from_file_and_cache(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    mock_git_valkey_cache,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG

    client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw"
    )

    assert len(mock_git_valkey_cache.cache) == 1
