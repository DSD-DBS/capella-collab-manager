# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import base64
import io
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
                f"https://example.com/api/v4/repos/test/project/actions/artifacts/12347/zip",
                status=200,
                body=get_zipfile(),
                content_type="application/zip",
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
    "git_type", [git_models.GitType.GITLAB, git_models.GitType.GITHUB]
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
)
def test_get_diagram_metadata(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@responses.activate
@pytest.mark.parametrize(
    "git_type,git_instance_api_url",
    [(git_models.GitType.GENERAL, "https://example.com/api/v4")],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
)
def test_get_diagrams_fails_without_git_instance(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 422
    assert response.json()["detail"]["err_code"] == "GIT_INSTANCE_UNSUPPORTED"


@responses.activate
@pytest.mark.parametrize(
    "git_type,git_instance_api_url",
    [(git_models.GitType.GITLAB, ""), (git_models.GitType.GITHUB, "")],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
)
def test_get_diagrams_fails_without_api_endpoint(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
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
    "git_type,job_status",
    [
        (git_models.GitType.GITLAB, "failed"),
        (git_models.GitType.GITHUB, "failure"),
    ],
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_rest_api_for_artifacts",
)
def test_get_diagrams_no_diagram_cache_job_found(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 400
    assert response.json()["detail"]["err_code"] == "FAILED_JOB_FOUND"


@responses.activate
@pytest.mark.parametrize(
    "git_type", [git_models.GitType.GITLAB, git_models.GitType.GITHUB]
)
@pytest.mark.usefixtures(
    "project_user",
    "git_instance",
    "git_model",
    "mock_git_rest_api_for_artifacts",
    "mock_git_diagram_cache_index_api",
    "mock_git_diagram_cache_svg",
)
@pytest.mark.usefixtures("project_user", "git_instance", "git_model")
def test_get_single_diagram(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams/_c90e4Hdf2d2UosmJBo0GTw",
    )

    assert response.status_code == 200
    assert response.content == EXAMPLE_SVG
