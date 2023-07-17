# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
from urllib import parse

import aiohttp
import fastapi
import requests
from fastapi import status

from capellacollab.config import config
from capellacollab.projects.toolmodels.modelsources.git.interface_class import (
    GitInterface,
    JobIDAtributes,
)

from .. import exceptions


class GitlabInterface(GitInterface):
    async def get_project_id_by_git_url(
        self,
    ) -> str:
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
                    raise fastapi.HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "err_code": "GITLAB_ACCESS_DENIED",
                            "reason": (
                                "The registered token has not enough permissions to access the Gitlab API.",
                                "Access scope 'read_api' is required. Please contact your project lead.",
                            ),
                        },
                    )
                if response.status == 404:
                    raise fastapi.HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail={
                            "err_code": "PROJECT_NOT_FOUND",
                            "reason": (
                                "We couldn't find the project in your Gitlab instance.",
                                f"Please make sure that a project with the encoded name '{project_name_encoded}' does exist.",
                            ),
                        },
                    )

                response.raise_for_status()
                return (await response.json())["id"]

    async def get_last_job_run_id_for_git_model(
        self,
        job_name: str,
    ) -> JobIDAtributes:
        self.check_git_instance_has_api_url()
        project_id = await self.get_project_id_by_git_url()
        for pipeline_id in await self.__get_last_pipeline_run_ids(project_id):
            if job := await self.__get_job_id_for_job_name(
                project_id,
                pipeline_id,
                job_name,
            ):
                return JobIDAtributes(project_id, job)

        raise exceptions.GitPipelineJobNotFoundError(job_name=job_name)

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
                            raise exceptions.GitPipelineFailedJobFoundError(
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
        self,
        trusted_file_path: str,
    ) -> bytes:
        self.check_git_instance_has_api_url()
        project_id = await self.get_project_id_by_git_url()
        response = requests.get(
            f"{self.git_instance.api_url}/projects/{project_id}/repository/files/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(self.git_model.revision, safe='')}",
            headers={"PRIVATE-TOKEN": self.git_model.password},
            timeout=config["requests"]["timeout"],
        )
        if response.status_code == 404:
            raise exceptions.GitRepositoryFileNotFoundError(
                filename=trusted_file_path
            )

        response.raise_for_status()
        return base64.b64decode(response.json()["content"])
