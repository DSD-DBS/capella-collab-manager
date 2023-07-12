# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import io
import json
import shutil
import tempfile
import typing as t
import zipfile
from urllib import parse

import fastapi
import requests
from fastapi import status

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.models as settings_git_models


def get_project_id_by_git_url(
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> str:
    # Project ID contains /{owner}/{repo_name}
    del git_instance  # unused
    return parse.urlparse(git_model.path).path


def get_last_job_run_id_for_git_model(
    job_name: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> tuple[settings_git_models.DatabaseGitInstance, str, tuple[str, str]]:
    project_id = get_project_id_by_git_url(git_model, git_instance)
    for job in get_last_pipeline_runs(project_id, git_model):
        if job["name"] == job_name:
            if job["conclusion"] == "success":
                return git_instance, project_id, (job["id"], job["created_at"])
            if job["conclusion"] == "failure" or job["expired"] == "False":
                raise fastapi.HTTPException(
                    status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "err_code": "FAILED_JOB_FOUND",
                        "reason": (
                            f"The last job with the name '{job_name}' on your branch has failed.",
                            "Please contact your administrator.",
                        ),
                    },
                )
    raise fastapi.HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "err_code": "PIPELINE_JOB_NOT_FOUND",
            "reason": (
                f"There was no job with the name '{job_name}' within the last 20 runs of the pipeline on your branch",
                "Please contact your administrator.",
            ),
        },
    )


def get_last_pipeline_runs(
    project_id: str,
    git_model: git_models.DatabaseGitModel,
) -> t.Any:
    response = requests.get(
        f"https://api.github.com/repos{project_id}/actions/runs?branch={parse.quote(git_model.revision, safe='')}&per_page=20",
        timeout=2,
    )

    if not response.ok:
        response = requests.get(
            f"https://api.github.com/repos{project_id}/actions/runs?branch={parse.quote(git_model.revision, safe='')}&per_page=20",
            headers={
                "Authorization": f"token {git_model.password}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Accept": "application/vnd.github+json",
            },
            timeout=2,
        )
    response.raise_for_status()
    return response.json()["workflow_runs"]


def get_artifact_from_job_as_content(
    project_id: str,
    job_id: str,
    trusted_path_to_artifact: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> bytes:
    return get_artifact_from_job(
        project_id, job_id, trusted_path_to_artifact, git_model, git_instance
    ).encode()


def get_artifact_from_job_as_json(
    project_id: str,
    job_id: str,
    trusted_path_to_artifact: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> dict:
    return json.loads(
        get_artifact_from_job(
            project_id,
            job_id,
            trusted_path_to_artifact,
            git_model,
            git_instance,
        )
    )


def get_artifact_from_job(
    project_id: str,
    job_id: str,
    trusted_path_to_artifact: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> str:
    response = requests.get(
        f"{git_instance.api_url}/repos{project_id}/actions/runs/{job_id}/artifacts",
        headers={
            "Authorization": f"token {git_model.password}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        },
        timeout=2,
    )
    response.raise_for_status()
    artifact_id = response.json()["artifacts"][0]["id"]

    if response.json()["artifacts"][0]["expired"] == "true":
        raise fastapi.HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "err_code": "ARTIFACT_EXPIRED",
                "reason": (
                    "The latest artifact you are requesting expired. Please rerun your pipline and contact your administrator."
                ),
            },
        )
    artifact_response = requests.get(
        f"{git_instance.api_url}/repos{project_id}/actions/artifacts/{artifact_id}/zip",
        headers={
            "Authorization": f"token {git_model.password}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        },
        timeout=2,
    )
    artifact_response.raise_for_status()

    return get_file_content(artifact_response, trusted_path_to_artifact)


def get_file_content(
    response: requests.Response, trusted_file_path: str
) -> str:
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        temp_dir = tempfile.mkdtemp()
        zip_ref.extractall(temp_dir)
        with open(
            temp_dir + "/" + trusted_file_path.split("/")[-1],
            encoding="utf-8",
        ) as file:
            content = file.read()
        shutil.rmtree(temp_dir)
        return content


def get_file_from_repository(
    trusted_file_path: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> bytes:
    project_id = get_project_id_by_git_url(git_model, git_instance)
    public_response = requests.get(
        f"{git_instance.api_url}/repos{project_id}/contents/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(git_model.revision, safe='')}",
        timeout=2,
    )
    if public_response.ok:
        response = public_response
    else:
        response = requests.get(
            f"{git_instance.api_url}/repos{project_id}/contents/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(git_model.revision, safe='')}",
            headers={
                "Authorization": f"token {git_model.password}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Accept": "application/vnd.github+json",
            },
            timeout=2,
        )
    response.raise_for_status()
    return base64.b64decode(response.json()["content"])
