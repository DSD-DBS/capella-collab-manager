# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
import datetime
import json
import typing as t

import requests

import capellacollab.projects.toolmodels.modelsources.git.models as git_models
import capellacollab.settings.modelsources.git.models as settings_git_models

from .. import exceptions

if t.TYPE_CHECKING:
    from capellambse import diagram_cache


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

    @abc.abstractmethod
    async def get_project_id_by_git_url(self) -> str:
        pass

    @abc.abstractmethod
    async def get_last_job_run_id_for_git_model(
        self, job_name: str, project_id: str | None = None
    ) -> tuple[str, str]:
        pass

    @abc.abstractmethod
    def get_artifact_from_job_as_json(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> dict:
        pass

    @abc.abstractmethod
    def get_artifact_from_job_as_content(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> bytes:
        pass

    @abc.abstractmethod
    async def get_file_from_repository(
        self,
        project_id: str,
        trusted_file_path: str,
        revision: str | None = None,
    ) -> bytes:
        pass

    @abc.abstractmethod
    def get_last_updated_for_file_path(
        self, project_id: str, file_path: str, revision: str | None
    ) -> datetime.datetime | None:
        pass

    async def get_file_from_repository_or_artifacts_as_json(
        self,
        trusted_file_path: str,
        job_name: str,
        revision: str | None = None,
    ) -> tuple[datetime.datetime, list[diagram_cache.IndexEntry]]:
        (
            last_updated,
            result,
        ) = await self.get_file_from_repository_or_artifacts(
            trusted_file_path, job_name, revision
        )
        return (last_updated, json.loads(result.decode("utf-8")))

    async def get_file_from_repository_or_artifacts(
        self,
        trusted_file_path: str,
        job_name: str,
        revision: str | None = None,
    ) -> tuple[t.Any, bytes]:
        project_id = await self.get_project_id_by_git_url()
        try:
            return (
                self.get_last_updated_for_file_path(
                    project_id,
                    trusted_file_path,
                    revision=revision,
                ),
                await self.get_file_from_repository(
                    project_id, trusted_file_path, revision
                ),
            )
        except (requests.HTTPError, exceptions.GitRepositoryFileNotFoundError):
            pass

        job_id, last_updated = await self.get_last_job_run_id_for_git_model(
            job_name, project_id
        )
        return (
            last_updated,
            self.get_artifact_from_job_as_content(
                project_id, job_id, trusted_file_path
            ),
        )
