# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.crud as settings_git_crud
import capellacollab.settings.modelsources.git.models as settings_git_models

from ..github import handler as github_handler
from ..gitlab import handler as gitlab_handler
from . import exceptions, handler


class GitHandlerFactory:
    @staticmethod
    def create_git_handler(
        db: orm.Session, git_model: git_models.DatabaseGitModel
    ) -> handler.GitHandler:
        git_instance = GitHandlerFactory.get_git_instance_for_git_model(
            db, git_model
        )
        match git_instance.type:
            case settings_git_models.GitType.GITLAB:
                return gitlab_handler.GitlabHandler(git_model, git_instance)
            case settings_git_models.GitType.GITHUB:
                return github_handler.GithubHandler(git_model, git_instance)
            case _:
                raise exceptions.GitInstanceUnsupportedError(
                    instance_name=str(git_instance.type)
                )

    @staticmethod
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
        raise exceptions.NoMatchingGitInstanceError
