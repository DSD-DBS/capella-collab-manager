# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import requests
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.crud as settings_git_crud
import capellacollab.settings.modelsources.git.models as settings_git_models

from .github import interface as github_interface
from .gitlab import interface as gitlab_interface


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
            print(instance)
            return instance
    raise fastapi.HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "reason": (
                "No matching git instance was found for the primary git model.",
                "Please contact your administrator.",
            ),
        },
    )


def git_instance_is_gitlab(
    git_instance: settings_git_models.DatabaseGitInstance,
) -> bool:
    return git_instance.type == settings_git_models.GitType.GITLAB


def git_instance_is_github(
    git_instance: settings_git_models.DatabaseGitInstance,
) -> bool:
    return git_instance.type == settings_git_models.GitType.GITHUB


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


def get_file_from_repository(
    db: orm.Session,
    trusted_file_path: str,
    git_model: git_models.DatabaseGitModel,
) -> requests.Response:
    git_instance = get_git_instance_for_git_model(db, git_model)
    check_git_instance_has_api_url(git_instance)
    if git_instance_is_gitlab(git_instance):
        project_id = gitlab_interface.get_project_id_by_git_url(
            git_model, git_instance
        )
        return gitlab_interface.__get_file_from_repository(
            project_id, trusted_file_path, git_model, git_instance
        )
    elif git_instance_is_github(git_instance):
        project_id = github_interface.get_project_id_by_git_url(
            git_model, git_instance
        )
        return github_interface.get_file_from_repository(
            project_id, trusted_file_path, git_model, git_instance
        )
    else:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "err_code": "INSTANCE_IS_NO_GIT_INSTANCE",
                "reason": (
                    "The used Git instance is neither a Gitlab nor a Github instance.",
                ),
            },
        )
