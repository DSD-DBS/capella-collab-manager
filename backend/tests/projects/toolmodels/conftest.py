# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import json
import re
import typing as t

import pytest
import responses
from aioresponses import aioresponses
from sqlalchemy import orm

import capellacollab.projects.models as project_models
import capellacollab.projects.toolmodels.crud as toolmodels_crud
import capellacollab.projects.toolmodels.models as toolmodels_models
import capellacollab.projects.toolmodels.modelsources.git.crud as project_git_crud
import capellacollab.projects.toolmodels.modelsources.git.models as project_git_models
import capellacollab.projects.toolmodels.modelsources.t4c.crud as models_t4c_crud
import capellacollab.projects.toolmodels.modelsources.t4c.models as models_t4c_models
import capellacollab.settings.modelsources.git.crud as git_crud
import capellacollab.settings.modelsources.git.models as git_models
import capellacollab.settings.modelsources.t4c.crud as settings_t4c_crud
import capellacollab.settings.modelsources.t4c.models as t4c_models
import capellacollab.settings.modelsources.t4c.repositories.crud as settings_t4c_repositories_crud
import capellacollab.settings.modelsources.t4c.repositories.interface as t4c_repositories_interface
import capellacollab.settings.modelsources.t4c.repositories.models as settings_t4c_repositories_models
import capellacollab.tools.crud as tools_crud
import capellacollab.tools.models as tools_models
from capellacollab.core import credentials


@pytest.fixture(name="capella_tool_version", params=["6.0.0"])
def fixture_capella_tool_version(
    db: orm.Session,
    request: pytest.FixtureRequest,
) -> tools_models.DatabaseVersion:
    return tools_crud.get_version_by_tool_id_version_name(
        db, tools_crud.get_tool_by_name(db, "Capella").id, request.param
    )


@pytest.fixture(name="capella_model")
def fixture_capella_model(
    db: orm.Session,
    project: project_models.DatabaseProject,
    capella_tool_version: tools_models.DatabaseVersion,
) -> toolmodels_models.DatabaseToolModel:
    model = toolmodels_models.PostCapellaModel(
        name="test", description="test", tool_id=capella_tool_version.tool.id
    )
    return toolmodels_crud.create_model(
        db, project, model, capella_tool_version.tool, capella_tool_version
    )


@pytest.fixture(
    name="git_type",
    params=[git_models.GitType.GITLAB],
)
def fixture_git_type(request: pytest.FixtureRequest) -> git_models.GitType:
    return request.param


@pytest.fixture(name="git_response_status", params=[200])
def fixture_git_response_status(request: pytest.FixtureRequest) -> int:
    return request.param


@pytest.fixture(
    name="git_instance_api_url", params=["https://example.com/api/v4"]
)
def fixture_git_instance_api_url(
    request: pytest.FixtureRequest,
) -> str:
    return request.param


@pytest.fixture(name="git_instance")
def fixture_git_instance(
    db: orm.Session, git_type: git_models.GitType, git_instance_api_url: str
) -> git_models.DatabaseGitInstance:
    git_instance = git_models.DatabaseGitInstance(
        name="test",
        url="https://example.com/test/project",
        api_url=git_instance_api_url,
        type=git_type,
    )
    return git_crud.create_git_instance(db, git_instance)


@pytest.fixture(name="git_model")
def fixture_git_models(
    db: orm.Session, capella_model: toolmodels_models.DatabaseToolModel
) -> project_git_models.DatabaseGitModel:
    git_model = project_git_models.PostGitModel(
        path="https://example.com/test/project",
        entrypoint="test/test.aird",
        revision="main",
        username="user",
        password="password",
    )
    return project_git_crud.add_git_model_to_capellamodel(
        db, capella_model, git_model
    )


@pytest.fixture(name="job_status", params=["success"])
def fixture_job_status(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(name="job_name", params=["update_capella_diagram_cache"])
def fixture_job_name(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture(name="mock_git_rest_api_for_artifacts")
def fixture_mock_git_rest_api_for_artifacts(
    job_status: str, git_type: git_models.GitType, job_name: str
):
    pipeline_ids = ["12345", "12346"]
    match git_type:
        case git_models.GitType.GITLAB:
            with aioresponses() as mocked:
                mocked.get(
                    "https://example.com/api/v4/projects/test%2Fproject",
                    status=200,
                    payload={"id": "10000"},
                )

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
                                "name": job_name,
                                "status": job_status,
                                "started_at": "2023-02-04T02:55:17.788000+00:00",
                                "id": "00002",
                            },
                        ],
                    )

                yield mocked
        case git_models.GitType.GITHUB:
            artifact_id = 12347
            responses.get(
                "https://example.com/api/v4/repos/test/project/actions/runs?branch=main&per_page=20",
                status=200,
                json={
                    "workflow_runs": [
                        {
                            "id": _id,
                            "name": job_name,
                            "conclusion": job_status,
                            "created_at": "2050-07-23T09:30:47Z",
                        }
                        for _id in pipeline_ids
                    ],
                },
            )
            responses.get(
                f"https://example.com/api/v4/repos/test/project/actions/runs/{pipeline_ids[0]}/artifacts",
                status=200,
                json={"artifacts": [{"id": artifact_id, "expired": "false"}]},
            )
            yield responses


@pytest.fixture(name="git_query_params")
def fixture_git_query_params(request: pytest.FixtureRequest) -> t.List[dict]:
    return request.param


def github_commit_api_callback(request):
    response_body = [
        {
            "sha": "43bf21488c5cc309af0ec635a8698b8509379527",
            "commit": {
                "author": {
                    "name": "test-name",
                    "email": "test-email",
                    "date": "2050-06-26T13:46:21Z",
                },
                "committer": {
                    "name": "test-name",
                    "email": "test-email",
                    "date": "2050-07-03T09:50:57Z",
                },
                "message": "test: Test commit message",
            },
        }
    ]
    return (200, {}, json.dumps(response_body))


@pytest.fixture(name="mock_git_get_commit_information_api")
def fixture_mock_git_get_commit_information_api(
    request: pytest.FixtureRequest,
    git_type: git_models.GitType,
    git_response_status: int,
    git_query_params: t.List[dict],
):
    match git_type:
        case git_models.GitType.GITLAB:
            for params in git_query_params:
                responses.get(
                    "https://example.com/api/v4/projects/10000/repository/commits",
                    status=git_response_status,
                    json=[
                        {
                            "id": "ee85bc253111b7a8ca2ce5aa26b8f5f36325f48a",
                            "created_at": "2050-04-11T10:09:59.000+02:00",
                            "title": "test: Test commit message",
                            "message": "test: Test commit message\n",
                            "author_name": "test-name",
                            "author_email": "test-email",
                            "authored_date": "2050-04-11T10:09:59.000+02:00",
                            "committer_name": "test-name",
                            "committer_email": "test-email",
                            "committed_date": "2050-04-11T10:09:59.000+02:00",
                        }
                    ],
                    match=[responses.matchers.query_param_matcher(params)],
                )
        case git_models.GitType.GITHUB:
            for params in git_query_params:
                responses.get(
                    "https://example.com/api/v4/repos/test/project/commits",
                    status=git_response_status,
                    json=[
                        {
                            "sha": "43bf21488c5cc309af0ec635a8698b8509379527",
                            "commit": {
                                "author": {
                                    "name": "test-name",
                                    "email": "test-email",
                                    "date": "2050-06-26T13:46:21Z",
                                },
                                "committer": {
                                    "name": "test-name",
                                    "email": "test-email",
                                    "date": "2050-07-03T09:50:57Z",
                                },
                                "message": "test: Test commit message",
                            },
                        }
                    ],
                    match=[responses.matchers.query_param_matcher(params)],
                )


@pytest.fixture(name="t4c_repository")
def fixture_t4c_repository(
    db: orm.Session,
) -> settings_t4c_repositories_models.DatabaseT4CRepository:
    t4c_instance = settings_t4c_crud.get_t4c_instances(db)[0]
    return settings_t4c_repositories_crud.create_t4c_repository(
        db=db, repo_name="test", instance=t4c_instance
    )


@pytest.fixture(name="t4c_model")
def fixture_t4c_model(
    db: orm.Session,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_repository: settings_t4c_repositories_models.DatabaseT4CRepository,
) -> models_t4c_models.DatabaseT4CModel:
    return models_t4c_crud.create_t4c_model(
        db, capella_model, t4c_repository, "default"
    )


@pytest.fixture(name="mock_add_user_to_t4c_repository")
def fixture_mock_add_user_to_t4c_repository(monkeypatch: pytest.MonkeyPatch):
    def mock_add_user_to_repository(
        instance: t4c_models.DatabaseT4CInstance,
        repository_name: str,
        username: str,
        password: str = credentials.generate_password(),
        is_admin: bool = False,
    ):
        return {}

    monkeypatch.setattr(
        t4c_repositories_interface,
        "add_user_to_repository",
        mock_add_user_to_repository,
    )
