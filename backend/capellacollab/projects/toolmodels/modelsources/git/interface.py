# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0


import fastapi
from fastapi import status
from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.crud as settings_git_crud
import capellacollab.settings.modelsources.git.models as settings_git_models

from . import interface_class
from .github.interface import GithubInterface
from .gitlab.interface import GitlabInterface


def get_git_class(
    db: orm.Session, git_model: git_models.DatabaseGitModel
) -> interface_class.GitInterface:
    git_instance = get_git_instance_for_git_model(db, git_model)
    match git_instance.type:
        case settings_git_models.GitType.GITLAB:
            return GitlabInterface(git_model, git_instance)
        case settings_git_models.GitType.GITHUB:
            return GithubInterface(git_model, git_instance)
        case _:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "err_code": "GIT_INSTANCE_UNSUPPORTED",
                    "reason": (
                        "The used Git instance is neither a Gitlab nor a Github instance.",
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
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "reason": (
                "No matching git instance was found for the primary git model.",
                "Please contact your administrator.",
            ),
        },
    )
