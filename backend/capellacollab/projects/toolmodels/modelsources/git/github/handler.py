# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import datetime
import io
import typing as t
import zipfile
from urllib import parse

import aiohttp
import asyncer

from capellacollab.configuration.app import config

from .. import exceptions as git_exceptions
from ..handler import handler


class GitHubHandler(handler.GitHandler):
    @classmethod
    async def get_repository_id_by_git_url(cls, path: str, *_) -> str:
        # Project ID has the format '{owner}/{repo_name}'
        return parse.urlparse(path).path[1:]

    async def get_last_successful_job_run(
        self, job_name: str
    ) -> tuple[str, datetime.datetime]:
        jobs = await self.get_last_pipeline_runs()
        if latest_job := self.__get_latest_successful_job(jobs, job_name):
            created_at = datetime.datetime.fromisoformat(
                latest_job["created_at"]
            )
            return (str(latest_job["id"]), created_at)

        raise git_exceptions.GitPipelineJobNotFoundError(
            job_name=job_name, revision=self.revision
        )

    async def __get_file_from_repository(
        self,
        trusted_file_path: str,
        revision: str,
        headers: dict[str, str] | None = None,
    ) -> t.Any:
        """Get a file from a GitHub repository

        Returns
        -------
        t.Any
            File content as json
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/{self.repository_id}/contents/{parse.quote(trusted_file_path)}?ref={parse.quote(revision, safe='')}",
                timeout=config.requests.timeout,
                headers=headers,
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def get_file_from_repository(
        self, trusted_file_path: str, revision: str | None = None
    ) -> bytes:
        """
        If a repository is public but the permissions are not set correctly, you might be able to download the file without authentication
        but get an error when trying to load it authenticated.

        For that purpose first we try to reach it with authentication and only if that fails try to get the file unauthenticated.
        """
        if self.password:
            try:
                json = await self.__get_file_from_repository(
                    trusted_file_path,
                    revision=revision or self.revision,
                    headers=self.__get_headers(),
                )
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    raise git_exceptions.GitRepositoryFileNotFoundError(
                        filename=trusted_file_path
                    ) from None

        try:
            json = await self.__get_file_from_repository(
                trusted_file_path,
                revision=revision or self.revision,
                headers=self.__get_headers(include_credentials=False),
            )
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                raise git_exceptions.GitRepositoryFileNotFoundError(
                    filename=trusted_file_path
                ) from None
            raise
        return base64.b64decode(json["content"])

    async def get_last_pipeline_runs(self) -> t.Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/{self.repository_id}/actions/runs?branch={parse.quote(self.revision, safe='')}&per_page=20",
                headers=(self.__get_headers() if self.password else None),
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                return (await response.json())["workflow_runs"]

    async def get_artifact_from_job(
        self, job_id: str, trusted_path_to_artifact: str
    ) -> bytes:
        artifact = await self.__get_latest_artifact_metadata(job_id)
        artifact_id = artifact["id"]

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/{self.repository_id}/actions/artifacts/{artifact_id}/zip",
                headers=self.__get_headers(),
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                content = await response.content.read()

                return await asyncer.asyncify(self.__get_file_content)(
                    content, trusted_path_to_artifact
                )

    async def get_last_updated_for_file(
        self, file_path: str, revision: str | None = None
    ) -> datetime.datetime:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/{self.repository_id}/commits?path={file_path}&sha={revision or self.revision}",
                headers=(self.__get_headers() if self.password else None),
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                json = await response.json()
                if len(json) == 0:
                    raise git_exceptions.GitRepositoryFileNotFoundError(
                        filename=file_path
                    )
                return datetime.datetime.fromisoformat(
                    json[0]["commit"]["author"]["date"]
                )

    async def get_started_at_for_job(self, job_id: str) -> datetime.datetime:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/{self.repository_id}/actions/runs/{parse.quote(job_id, safe='')}",
                headers=self.__get_headers(),
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                return datetime.datetime.fromisoformat(
                    (await response.json())["created_at"]
                )

    def __get_file_content(
        self, content: bytes, trusted_file_path: str
    ) -> bytes:
        with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
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

    async def __get_latest_artifact_metadata(self, job_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/repos/{self.repository_id}/actions/runs/{parse.quote(job_id, safe='')}/artifacts",
                headers=self.__get_headers(),
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                artifact = (await response.json())["artifacts"][0]
                if artifact["expired"] == "true":
                    raise git_exceptions.GitHubArtifactExpiredError()
                return artifact

    def __get_headers(self, include_credentials: bool = True) -> dict:
        headers = {
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        }
        if include_credentials:
            headers["Authorization"] = f"token {self.password}"

        return headers
