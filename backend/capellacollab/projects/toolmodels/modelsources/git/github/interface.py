# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
from urllib import parse

import requests

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.models as settings_git_models


def get_project_id_by_git_url(
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> str:
    # Project ID contains {owner}/{repo_name}
    del git_instance  # unused
    return parse.urlparse(git_model.path).path


def get_file_from_repository(
    project_id: str,
    trusted_file_path: str,
    git_model: git_models.DatabaseGitModel,
    git_instance: settings_git_models.DatabaseGitInstance,
) -> bytes:
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
