# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import collections
from abc import abstractmethod

import requests

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.models as settings_git_models

from . import exceptions

JobIDAtributes = collections.namedtuple(
    "JobIDAtributes", ["projectID", "jobIDandDatetuple"]
)


class GitInterface:
    def __init__(
        self,
        git_model: git_models.DatabaseGitModel,
        git_instance: settings_git_models.DatabaseGitInstance,
    ) -> None:
        self.git_model = git_model
        self.git_instance = git_instance

    def check_git_instance_has_api_url(self):
        if not self.git_instance.api_url:
            raise exceptions.GitInstanceAPIEndpointNotFoundError()

    @abstractmethod
    async def get_project_id_by_git_url(self) -> str:
        pass

    @abstractmethod
    async def get_last_job_run_id_for_git_model(
        self,
        job_name: str,
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
        self,
        trusted_file_path: str,
    ) -> requests.Response:
        pass
