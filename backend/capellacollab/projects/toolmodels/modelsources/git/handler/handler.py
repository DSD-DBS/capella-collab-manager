# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import collections
import typing as t
from abc import abstractmethod

import requests

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.models as settings_git_models

from .. import exceptions

JobIdAttributes = collections.namedtuple(
    "JobIdAttributes", ["projectId", "jobIdAndDateTuple"]
)


class GitHandler:
    def __init__(
        self,
        git_model: git_models.DatabaseGitModel,
        git_instance: settings_git_models.DatabaseGitInstance,
    ) -> None:
        self.git_model = git_model
        self.git_instance = git_instance
        self.check_git_instance_has_api_url()

    def check_git_instance_has_api_url(self):
        if not self.git_instance.api_url:
            raise exceptions.GitInstanceAPIEndpointNotFoundError()

    @abstractmethod
    async def get_project_id_by_git_url(self) -> str:
        pass

    @abstractmethod
    async def get_last_job_run_id_for_git_model(
        self, job_name: str, project_id: t.Optional[str]
    ) -> tuple[str, tuple[str, str]]:
        pass

    @abstractmethod
    def get_artifact_from_job_as_json(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> dict:
        pass

    @abstractmethod
    def get_artifact_from_job_as_content(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> bytes:
        pass

    @abstractmethod
    async def get_file_from_repository(
        self, project_id: str, trusted_file_path: str
    ) -> (requests.Response, bytes):
        pass

    async def get_file_from_repository_or_artifacts(
        self, trusted_file_path: str, job_name: str | None
    ) -> bytes:
        project_id = await self.get_project_id_by_git_url()
        response, file = await self.get_file_from_repository(
            project_id, trusted_file_path
        )
        if file:
            return file
        if job_name:
            _, job_attributes = await self.get_last_job_run_id_for_git_model(
                job_name, project_id
            )
            return self.get_artifact_from_job_as_content(
                project_id, job_attributes[0], trusted_file_path
            )
        if response.status_code == 404:
            raise exceptions.GitRepositoryFileNotFoundError(
                filename=trusted_file_path
            )
        response.raise_for_status()
        return None
