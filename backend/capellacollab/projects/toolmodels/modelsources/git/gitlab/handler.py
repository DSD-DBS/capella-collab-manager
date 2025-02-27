# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import datetime
from urllib import parse

import aiohttp

from capellacollab.configuration.app import config

from .. import exceptions as git_exceptions
from ..handler import handler
from . import exceptions


class GitlabHandler(handler.GitHandler):
    @classmethod
    async def get_repository_id_by_git_url(
        cls, path: str, password: str, api_url: str
    ) -> str:
        project_name_encoded = parse.quote(
            parse.urlparse(path).path.lstrip("/").removesuffix(".git"),
            safe="",
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{api_url}/projects/{project_name_encoded}",
                headers={"PRIVATE-TOKEN": password},
                timeout=config.requests.timeout,
            ) as response:
                if response.status == 403:
                    raise exceptions.GitlabAccessDeniedError
                if response.status == 404:
                    raise exceptions.GitlabProjectNotFoundError(
                        project_name=project_name_encoded
                    )

                response.raise_for_status()
                return (await response.json())["id"]

    async def get_last_successful_job_run(
        self, job_name: str
    ) -> tuple[str, datetime.datetime]:
        for pipeline_id in await self.__get_last_pipeline_run_ids():
            if job := await self.__get_job_id_for_job_name(
                pipeline_id, job_name
            ):
                return (str(job[0]), job[1])

        raise git_exceptions.GitPipelineJobNotFoundError(
            job_name=job_name, revision=self.revision
        )

    async def get_last_updated_for_file(
        self, file_path: str, revision: str | None = None
    ) -> datetime.datetime:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/projects/{self.repository_id}/repository/commits?ref_name={revision or self.revision}&path={file_path}",
                headers={"PRIVATE-TOKEN": self.password},
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                json = await response.json()
                if len(json) == 0:
                    raise git_exceptions.GitRepositoryFileNotFoundError(
                        filename=file_path
                    )
                return datetime.datetime.fromisoformat(
                    json[0]["authored_date"]
                )

    async def get_started_at_for_job(self, job_id: str) -> datetime.datetime:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/projects/{self.repository_id}/jobs/{parse.quote(job_id, safe='')}",
                headers={"PRIVATE-TOKEN": self.password},
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()
                return datetime.datetime.fromisoformat(
                    (await response.json())["started_at"]
                )

    async def __get_last_pipeline_run_ids(self) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/projects/{self.repository_id}/pipelines?ref={parse.quote(self.revision, safe='')}&per_page=20",
                headers={"PRIVATE-TOKEN": self.password},
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()

                return [pipeline["id"] for pipeline in await response.json()]

    async def __get_job_id_for_job_name(
        self, pipeline_id: str, job_name: str
    ) -> tuple[str, datetime.datetime] | None:
        """Search for a job by name in a pipeline"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/projects/{self.repository_id}/pipelines/{pipeline_id}/jobs",
                headers={"PRIVATE-TOKEN": self.password},
                timeout=config.requests.timeout,
            ) as response:
                response.raise_for_status()

                for job in await response.json():
                    if job["name"] == job_name:
                        if job["status"] == "success":
                            started_at = datetime.datetime.fromisoformat(
                                job["started_at"]
                            )
                            return job["id"], started_at
                        if job["status"] == "failed":
                            raise git_exceptions.GitPipelineJobUnsuccessfulError(
                                job_name, "failed"
                            )

                return None

    async def get_artifact_from_job(
        self, job_id: str, trusted_path_to_artifact: str
    ) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/projects/{self.repository_id}/jobs/{parse.quote(job_id, safe='')}/artifacts/{trusted_path_to_artifact}",
                headers={"PRIVATE-TOKEN": self.password},
                timeout=config.requests.timeout,
            ) as response:
                if response.status == 404:
                    raise git_exceptions.GitRepositoryFileNotFoundError(
                        filename=trusted_path_to_artifact
                    )

                response.raise_for_status()
                return await response.content.read()

    async def get_file_from_repository(
        self, trusted_file_path: str, revision: str | None = None
    ) -> bytes:
        branch = revision if revision else self.revision

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/projects/{self.repository_id}/repository/files/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(branch, safe='')}",
                headers={"PRIVATE-TOKEN": self.password},
                timeout=config.requests.timeout,
            ) as response:
                if response.status == 404:
                    raise git_exceptions.GitRepositoryFileNotFoundError(
                        filename=trusted_file_path
                    )
                response.raise_for_status()

                return base64.b64decode((await response.json())["content"])
