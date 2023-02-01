# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from urllib import parse

import fastapi
import requests
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.crud as settings_git_crud
import capellacollab.settings.modelsources.git.models as settings_git_models


def get_last_job_run_id_for_git_model(
    db: orm.Session, job_name: str, git_model: git_models.DatabaseGitModel
) -> tuple[settings_git_models.DatabaseGitInstance, str, tuple[str, str]]:
    git_instance = get_git_instance_for_git_model(db, git_model)
    check_git_instance_is_gitlab(git_instance)
    check_git_instance_has_api_url(git_instance)
    project_id = get_project_id_by_git_url(git_model, git_instance)
    for pipeline_id in get_last_pipeline_run_ids(
        project_id, git_model, git_instance
    ):
        if job := get_job_id_for_job_name(
            project_id, pipeline_id, job_name, git_model, git_instance
        ):
            return git_instance, project_id, job

    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "err_code": "NO_SUCCESSFUL_JOB",
            "reason": (
                f"There was no successful '{job_name}' job within the last 20 runs of the pipeline",
                "Please contact your administrator.",
            ),
        },
    )


def get_git_instance_for_git_model(
    db: orm.Session, git_model: git_models.DatabaseGitModel
) -> settings_git_models.DatabaseGitInstance:
    """Get the corresponding git instance for a git model
    The git instance is selected via the longest common prefix match.
    """

    instances_sorted_by_len = sorted(
        settings_git_crud.get_git_instances(db),
        key=lambda instance: len(instance.url),
        reverse=True,
    )

    for instance in instances_sorted_by_len:
        if git_model.path.startswith(instance.url):
            return instance
    raise fastapi.HTTPException(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "reason": (
                "No matching git instance was found for the primary git model.",
                "Please contact your administrator.",
            ),
        },
    )


def check_git_instance_is_gitlab(
    git_instance: settings_git_models.DatabaseGitInstance,
):
    if git_instance.type != settings_git_models.GitType.GITLAB:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "err_code": "INSTANCE_IS_NO_GITLAB_INSTANCE",
                "reason": (
                    "The used Git instance is not a Gitlab instance.",
                    "Only Gitlab instances are supported.",
                ),
            },
        )


def check_git_instance_has_api_url(
    git_instance: settings_git_models.DatabaseGitInstance,
):
    if not git_instance.api_url:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "err_code": "GIT_INSTANCE_NO_API_ENDPOINT_DEFINED",
                "reason": (
                    "The used Git instance has no API endpoint defined.",
                    "Please contact your administrator.",
                ),
            },
        )


def get_project_id_by_git_url(
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> str:
    project_name_encoded = parse.quote(
        parse.urlparse(git_model.path).path.lstrip("/"), safe=""
    )
    response = requests.get(
        f"{git_instance.api_url}/projects/{project_name_encoded}",
        headers={"PRIVATE-TOKEN": git_model.password},
        timeout=2,
    )
    response.raise_for_status()

    return response.json()["id"]


def get_last_pipeline_run_ids(
    project_id: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> list[str]:
    response = requests.get(
        f"{git_instance.api_url}/projects/{project_id}/pipelines?ref={parse.quote(git_model.revision, safe='')}&per_page=20",
        headers={"PRIVATE-TOKEN": git_model.password},
        timeout=2,
    )
    response.raise_for_status()

    return [pipeline["id"] for pipeline in response.json()]


def get_job_id_for_job_name(
    project_id: str,
    pipeline_id: str,
    job_name: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> tuple[str, str] | None:
    response = requests.get(
        f"{git_instance.api_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs",
        headers={"PRIVATE-TOKEN": git_model.password},
        timeout=2,
    )
    response.raise_for_status()

    for job in response.json():
        if job["name"] == job_name:
            if job["status"] == "success":
                return job["id"], job["started_at"]

    return None


def get_artifact_from_job_as_json(
    project_id: str,
    job_id: str,
    trusted_path_to_artifact: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> dict:
    return get_artifact_from_job(
        project_id, job_id, trusted_path_to_artifact, git_model, git_instance
    ).json()


def get_artifact_from_job_as_content(
    project_id: str,
    job_id: str,
    trusted_path_to_artifact: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> bytes:
    return get_artifact_from_job(
        project_id, job_id, trusted_path_to_artifact, git_model, git_instance
    ).content


def get_artifact_from_job(
    project_id: str,
    job_id: str,
    trusted_path_to_artifact: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> requests.Response:
    response = requests.get(
        f"{git_instance.api_url}/projects/{project_id}/jobs/{job_id}/artifacts/{trusted_path_to_artifact}",
        headers={"PRIVATE-TOKEN": git_model.password},
        timeout=2,
    )
    response.raise_for_status()
    return response