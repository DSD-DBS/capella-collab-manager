# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import orm

import capellacollab.projects.toolmodels.modelsources.git.crud as git_crud
import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.crud as settings_git_crud
import capellacollab.settings.modelsources.git.models as settings_git_models

from ..github import handler as github_handler
from ..gitlab import handler as gitlab_handler
from . import exceptions, handler


class GitHandlerFactory:
    @staticmethod
    async def create_git_handler(
        db: orm.Session, git_model: git_models.DatabaseGitModel
    ) -> handler.GitHandler:
        """
        Create a git handler for the given git model.

        Args:
            db (orm.Session): Database session.
            git_model (git_models.DatabaseGitModel): The git model instance.

        Returns:
            handler.GitHandler: An instance of GitHandler.

        Raises:
            GitInstanceAPIEndpointNotFoundError: If the git instance API endpoint is not found.
            GitInstanceUnsupportedError: If the git instance type is unsupported.
        """
        git_instance = GitHandlerFactory.get_git_instance_for_git_model(
            db, git_model
        )

        if not git_instance.api_url:
            raise exceptions.GitInstanceAPIEndpointNotFoundError()

        if not git_model.repository_id:
            repository_id = await GitHandlerFactory._get_repository_id(
                git_model, git_instance
            )
            git_crud.update_git_model_repository_id(
                db, git_model, repository_id
            )

        return GitHandlerFactory._create_specific_git_handler(
            git_model, git_instance
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

    @staticmethod
    async def _get_repository_id(
        git_model: git_models.DatabaseGitModel,
        git_instance: settings_git_models.DatabaseGitInstance,
    ) -> str:
        if not (api_url := git_instance.api_url):
            raise exceptions.GitInstanceAPIEndpointNotFoundError()

        match git_instance.type:
            case settings_git_models.GitType.GITLAB:
                return await gitlab_handler.GitlabHandler.get_repository_id_by_git_url(
                    git_model.path, git_model.password, api_url
                )
            case settings_git_models.GitType.GITHUB:
                return await github_handler.GithubHandler.get_repository_id_by_git_url(
                    git_model.path, git_model.password
                )
            case _:
                raise exceptions.GitInstanceUnsupportedError(
                    instance_name=str(git_instance.type)
                )

    @staticmethod
    def _create_specific_git_handler(
        git_model: git_models.DatabaseGitModel,
        git_instance: settings_git_models.DatabaseGitInstance,
    ) -> handler.GitHandler:
        if not (api_url := git_instance.api_url):
            raise exceptions.GitInstanceAPIEndpointNotFoundError()
        if not (repository_id := git_model.repository_id):
            raise exceptions.GitRepositoryIdNotFoundError()

        match git_instance.type:
            case settings_git_models.GitType.GITLAB:
                return gitlab_handler.GitlabHandler(
                    git_model.path,
                    git_model.revision,
                    git_model.password,
                    api_url,
                    repository_id,
                )
            case settings_git_models.GitType.GITHUB:
                return github_handler.GithubHandler(
                    git_model.path,
                    git_model.revision,
                    git_model.password,
                    api_url,
                    repository_id,
                )
            case _:
                raise exceptions.GitInstanceUnsupportedError(
                    instance_name=str(git_instance.type)
                )
