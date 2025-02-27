# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import urllib.parse

from aioresponses import aioresponses

import capellacollab.settings.modelsources.git.models as git_models


def mock_git_get_commit_information_api(
    git_type: git_models.GitType,
    aiomock: aioresponses,
    path: str,
    response_status: int = 200,
    revision: str = "main",
):
    # https://github.com/pnuckowski/aioresponses/issues/231
    path = urllib.parse.quote(urllib.parse.quote(path, safe=""), safe="")
    revision = urllib.parse.quote(
        urllib.parse.quote(revision, safe=""), safe=""
    )

    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                f"https://example.com/api/v4/projects/10000/repository/commits?path={path}&ref_name={revision}",
                status=response_status,
                repeat=True,
                payload=[
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
            )
        case git_models.GitType.GITHUB:
            aiomock.get(
                f"https://example.com/api/v4/repos/test/project/commits?path={path}&sha={revision}",
                status=response_status,
                repeat=True,
                payload=[
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
            )


def mock_git_rest_api_for_artifacts(
    git_type: git_models.GitType,
    job_name: str,
    job_status: str,
    pipeline_ids: list[str],
    aiomock: aioresponses,
):
    match git_type:
        case git_models.GitType.GITLAB:
            aiomock.get(
                "https://example.com/api/v4/projects/test%2Fproject",
                status=200,
                repeat=True,
                payload={"id": "10000"},
            )

            aiomock.get(
                "https://example.com/api/v4/projects/10000/pipelines?per_page=20&ref=main",
                status=200,
                payload=[{"id": _id} for _id in pipeline_ids],
            )

            for _id in pipeline_ids:
                aiomock.get(
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
        case git_models.GitType.GITHUB:
            artifact_id = 12347
            aiomock.get(
                "https://example.com/api/v4/repos/test/project/actions/runs?branch=main&per_page=20",
                status=200,
                payload={
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

            if pipeline_ids:
                aiomock.get(
                    f"https://example.com/api/v4/repos/test/project/actions/runs/{pipeline_ids[0]}/artifacts",
                    status=200,
                    payload={
                        "artifacts": [{"id": artifact_id, "expired": "false"}]
                    },
                )
