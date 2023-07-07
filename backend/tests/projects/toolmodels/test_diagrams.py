# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
import responses
from aioresponses import aioresponses
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.settings.modelsources.git.crud as git_crud
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


@pytest.fixture(name="diagram_cache_job_status")
def fixture_diagram_cache_job_status(request: pytest.FixtureRequest):
    if hasattr(request, "param"):
        return request.param
    else:
        return "success"


@pytest.fixture()
def mock_gitlab_rest_api(diagram_cache_job_status: str):
    with aioresponses() as mocked:
        mocked.get(
            "https://example.com/api/v4/projects/test%2Fproject",
            status=200,
            payload={"id": "10000"},
        )

        pipeline_ids = ["12345", "12346"]
        mocked.get(
            "https://example.com/api/v4/projects/10000/pipelines?ref=main&per_page=20",
            status=200,
            payload=[{"id": _id} for _id in pipeline_ids],
        )

        for _id in pipeline_ids:
            mocked.get(
                f"https://example.com/api/v4/projects/10000/pipelines/{_id}/jobs",
                status=200,
                payload=[
                    {
                        "name": "test",
                        "status": "failure",
                        "started_at": "2023-02-04T02:55:17.788000+00:00",
                        "id": "00001",
                    },
                    {
                        "name": "update_capella_diagram_cache",
                        "status": diagram_cache_job_status,
                        "started_at": "2023-02-04T02:55:17.788000+00:00",
                        "id": "00002",
                    },
                ],
            )

        yield mocked


@pytest.fixture
def mock_gitlab_diagram_cache_index_api():
    responses.get(
        "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/diagram_cache/index.json",
        status=200,
        json=[
            {
                "name": "Diagram 1",
                "uuid": "_c90e4Hdf2d2UosmJBo0GTw",
                "success": True,
            },
            {
                "name": "Diagram 2",
                "uuid": "_VjvUMasdf2e2wVuAPh3ezQ",
                "success": True,
            },
        ],
    )


@pytest.fixture
def mock_gitlab_diagram_cache_svg():
    responses.get(
        "https://example.com/api/v4/projects/10000/jobs/00002/artifacts/diagram_cache/_c90e4Hdf2d2UosmJBo0GTw.svg",
        status=200,
        body=EXAMPLE_SVG,
    )


@responses.activate
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
    "mock_gitlab_diagram_cache_index_api",
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
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
)
def test_get_diagrams_fails_without_gitlab_instance(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 500
    assert (
        response.json()["detail"]["err_code"] == "INSTANCE_IS_NO_GIT_INSTANCE"
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
def test_get_diagrams_fails_without_api_endpoint(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 500
    assert (
        response.json()["detail"]["err_code"]
        == "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED"
    )


@responses.activate
@pytest.mark.parametrize(
    "diagram_cache_job_status",
    ["failure"],
)
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
)
def test_get_diagrams_no_diagram_cache_job_found(
    project: project_models.DatabaseProject,
    capella_model: toolmodels_models.CapellaModel,
    client: testclient.TestClient,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/diagrams",
    )

    assert response.status_code == 500
    assert response.json()["detail"]["err_code"] == "PIPELINE_JOB_NOT_FOUND"


@responses.activate
@pytest.mark.usefixtures(
    "project_user",
    "gitlab_instance",
    "git_model",
    "mock_gitlab_rest_api",
    "mock_gitlab_diagram_cache_svg",
)
@pytest.mark.usefixtures("project_user", "gitlab_instance", "git_model")
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
