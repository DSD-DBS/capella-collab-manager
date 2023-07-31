# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
from urllib import parse

import aiohttp
import requests

from capellacollab.config import config

from .. import exceptions as git_exceptions
from ..handler import handler
from . import exceptions


class GitlabHandler(handler.GitHandler):
    async def get_project_id_by_git_url(self) -> str:
        project_name_encoded = parse.quote(
            parse.urlparse(self.git_model.path)
            .path.lstrip("/")
            .removesuffix(".git"),
            safe="",
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.git_instance.api_url}/projects/{project_name_encoded}",
                headers={"PRIVATE-TOKEN": self.git_model.password},
                timeout=config["requests"]["timeout"],
            ) as response:
                if response.status == 403:
                    raise exceptions.GitlabAccessDeniedError
                if response.status == 404:
                    raise exceptions.GitlabProjectNotFoundError(
                        project_name=project_name_encoded
                    )

                response.raise_for_status()
                return (await response.json())["id"]

    async def get_last_job_run_id_for_git_model(
        self, job_name: str, project_id: str | None = None
    ) -> handler.JobIdAttributes:
        if not project_id:
            project_id = await self.get_project_id_by_git_url()
        for pipeline_id in await self.__get_last_pipeline_run_ids(project_id):
            if job := await self.__get_job_id_for_job_name(
                project_id,
                pipeline_id,
                job_name,
            ):
                return handler.JobIdAttributes(project_id, job)

        raise git_exceptions.GitPipelineJobNotFoundError(job_name=job_name)

    async def __get_last_pipeline_run_ids(
        self,
        project_id: str,
    ) -> list[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.git_instance.api_url}/projects/{project_id}/pipelines?ref={parse.quote(self.git_model.revision, safe='')}&per_page=20",
                headers={"PRIVATE-TOKEN": self.git_model.password},
                timeout=config["requests"]["timeout"],
            ) as response:
                response.raise_for_status()

                return [pipeline["id"] for pipeline in await response.json()]

    async def __get_job_id_for_job_name(
        self,
        project_id: str,
        pipeline_id: str,
        job_name: str,
    ) -> tuple[str, str] | None:
        """Search for a job by name in a pipeline"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.git_instance.api_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs",
                headers={"PRIVATE-TOKEN": self.git_model.password},
                timeout=config["requests"]["timeout"],
            ) as response:
                response.raise_for_status()

                for job in await response.json():
                    if job["name"] == job_name:
                        if job["status"] == "success":
                            return job["id"], job["started_at"]
                        if job["status"] == "failed":
                            raise git_exceptions.GitPipelineJobFailedError(
                                job_name
                            )

                return None

    def get_artifact_from_job_as_json(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> dict:
        return self.get_artifact_from_job(
            project_id,
            job_id,
            trusted_path_to_artifact,
        ).json()

    def get_artifact_from_job_as_content(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> bytes:
        return self.get_artifact_from_job(
            project_id,
            job_id,
            trusted_path_to_artifact,
        ).content

    def get_artifact_from_job(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> requests.Response:
        response = requests.get(
            f"{self.git_instance.api_url}/projects/{project_id}/jobs/{job_id}/artifacts/{trusted_path_to_artifact}",
            headers={"PRIVATE-TOKEN": self.git_model.password},
            timeout=config["requests"]["timeout"],
        )
        response.raise_for_status()
        return response

    async def get_file_from_repository(
        self, project_id: str, trusted_file_path: str
    ) -> bytes:
        response = requests.get(
            f"{self.git_instance.api_url}/projects/{project_id}/repository/files/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(self.git_model.revision, safe='')}",
            headers={"PRIVATE-TOKEN": self.git_model.password},
            timeout=config["requests"]["timeout"],
        )

        if response.status_code == 404:
            raise git_exceptions.GitRepositoryFileNotFoundError(
                filename=trusted_file_path
            )
        response.raise_for_status()

        return base64.b64decode(response.json()["content"])
