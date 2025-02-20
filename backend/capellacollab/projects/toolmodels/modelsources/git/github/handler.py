# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import datetime
import io
import typing as t
import zipfile
from urllib import parse

import requests

from capellacollab.configuration.app import config

from .. import exceptions as git_exceptions
from ..handler import handler


class GithubHandler(handler.GitHandler):
    @classmethod
    async def get_repository_id_by_git_url(cls, path: str, *_) -> str:
        # Project ID has the format '{owner}/{repo_name}'
        return parse.urlparse(path).path[1:]

    async def get_last_successful_job_run(
        self, job_name: str
    ) -> tuple[str, datetime.datetime]:
        jobs = self.get_last_pipeline_runs()
        if latest_job := self.__get_latest_successful_job(jobs, job_name):
            created_at = datetime.datetime.fromisoformat(
                latest_job["created_at"]
            )
            return (str(latest_job["id"]), created_at)

        raise git_exceptions.GitPipelineJobNotFoundError(
            job_name=job_name, revision=self.revision
        )

    def __get_file_from_repository(
        self,
        trusted_file_path: str,
        revision: str,
        headers: dict[str, str] | None = None,
    ) -> requests.Response:
        return requests.get(
            f"{self.api_url}/repos/{self.repository_id}/contents/{parse.quote(trusted_file_path)}?ref={parse.quote(revision, safe='')}",
            timeout=config.requests.timeout,
            headers=headers,
        )

    def get_file_from_repository(
        self, trusted_file_path: str, revision: str | None = None
    ) -> bytes:
        """
        If a repository is public but the permissions are not set correctly, you might be able to download the file without authentication
        but get an error when trying to load it authenticated.

        For that purpose first we try to reach it without authentication and only if that fails try to get the file authenticated.
        """
        response = self.__get_file_from_repository(
            trusted_file_path, revision or self.revision
        )

        if not response.ok and self.password:
            response = self.__get_file_from_repository(
                trusted_file_path,
                revision=revision or self.revision,
                headers=self.__get_headers(),
            )

        if response.status_code == 404:
            raise git_exceptions.GitRepositoryFileNotFoundError(
                filename=trusted_file_path
            )
        response.raise_for_status()

        return base64.b64decode(response.json()["content"])

    def get_last_pipeline_runs(self) -> t.Any:
        response = requests.get(
            f"{self.api_url}/repos/{self.repository_id}/actions/runs?branch={parse.quote(self.revision, safe='')}&per_page=20",
            headers=(self.__get_headers() if self.password else None),
            timeout=config.requests.timeout,
        )
        response.raise_for_status()
        return response.json()["workflow_runs"]

    def get_artifact_from_job(
        self, job_id: str, trusted_path_to_artifact: str
    ) -> bytes:
        artifact = self.__get_latest_artifact_metadata(job_id)
        artifact_id = artifact["id"]
        artifact_response = requests.get(
            f"{self.api_url}/repos/{self.repository_id}/actions/artifacts/{artifact_id}/zip",
            headers=self.__get_headers(),
            timeout=config.requests.timeout,
        )
        artifact_response.raise_for_status()

        return self.__get_file_content(
            artifact_response, trusted_path_to_artifact
        )

    def get_last_updated_for_file(
        self, file_path: str, revision: str | None = None
    ) -> datetime.datetime:
        response = requests.get(
            f"{self.api_url}/repos/{self.repository_id}/commits?path={file_path}&sha={revision or self.revision}",
            headers=(self.__get_headers() if self.password else None),
            timeout=config.requests.timeout,
        )
        response.raise_for_status()
        if len(response.json()) == 0:
            raise git_exceptions.GitRepositoryFileNotFoundError(
                filename=file_path
            )
        return datetime.datetime.fromisoformat(
            response.json()[0]["commit"]["author"]["date"]
        )

    def get_started_at_for_job(self, job_id: str) -> datetime.datetime:
        response = requests.get(
            f"{self.api_url}/repos/{self.repository_id}/actions/runs/{parse.quote(job_id, safe='')}",
            headers=self.__get_headers(),
            timeout=config.requests.timeout,
        )
        response.raise_for_status()
        return datetime.datetime.fromisoformat(response.json()["created_at"])

    def __get_file_content(
        self, response: requests.Response, trusted_file_path: str
    ) -> bytes:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            file_list = zip_file.namelist()

            try:
                file_index = file_list.index(trusted_file_path.split("/")[-1])
            except ValueError as e:
                raise git_exceptions.GitRepositoryFileNotFoundError(
                    filename=trusted_file_path
                ) from e

            with zip_file.open(file_list[file_index], "r") as file:
                return file.read()

    def __get_latest_successful_job(
        self, jobs: list, job_name: str
    ) -> dict | None:
        matched_jobs = [job for job in jobs if job["name"] == job_name]
        if not matched_jobs:
            raise git_exceptions.GitPipelineJobNotFoundError(
                job_name=job_name, revision=self.revision
            )
        matched_jobs.sort(key=lambda job: job["created_at"], reverse=True)
        if matched_jobs[0]["conclusion"] == "success":
            return matched_jobs[0]

        raise git_exceptions.GitPipelineJobUnsuccessfulError(
            job_name, matched_jobs[0]["conclusion"]
        )

    def __get_latest_artifact_metadata(self, job_id: str):
        response = requests.get(
            f"{self.api_url}/repos/{self.repository_id}/actions/runs/{parse.quote(job_id, safe='')}/artifacts",
            headers=self.__get_headers(),
            timeout=config.requests.timeout,
        )
        response.raise_for_status()
        artifact = response.json()["artifacts"][0]
        if artifact["expired"] == "true":
            raise git_exceptions.GithubArtifactExpiredError()
        return artifact

    def __get_headers(self) -> dict:
        return {
            "Authorization": f"token {self.password}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        }
