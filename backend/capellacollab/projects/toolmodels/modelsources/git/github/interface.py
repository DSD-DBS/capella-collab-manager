# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import io
import json
import typing as t
import zipfile
from urllib import parse

import fastapi
import requests
from fastapi import status

from capellacollab.config import config
from capellacollab.projects.toolmodels.modelsources.git.interface_class import (
    GitInterface,
    JobIDAtributes,
)

from .. import exceptions


class GithubInterface(GitInterface):
    def get_headers(self, password: str) -> dict:
        return {
            "Authorization": f"token {password}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Accept": "application/vnd.github+json",
        }

    async def get_project_id_by_git_url(
        self,
    ) -> str:
        # Project ID has the format '/{owner}/{repo_name}'
        return parse.urlparse(self.git_model.path).path

    async def get_last_job_run_id_for_git_model(
        self,
        job_name: str,
    ) -> JobIDAtributes:
        self.check_git_instance_has_api_url()
        project_id = await self.get_project_id_by_git_url()
        for job in self.get_last_pipeline_runs(project_id):
            if job["name"] == job_name:
                if job["conclusion"] == "success":
                    return JobIDAtributes(
                        project_id,
                        (job["id"], job["created_at"]),
                    )
                if job["conclusion"] == "failure" or job["expired"] == "False":
                    raise exceptions.GitPipelineFailedJobFoundError(job_name)
        raise exceptions.GitPipelineJobNotFoundError(job_name=job_name)

    def get_last_pipeline_runs(
        self,
        project_id: str,
    ) -> t.Any:
        if not self.git_model.password:
            response = requests.get(
                f"{self.git_instance.api_url}/repos{project_id}/actions/runs?branch={parse.quote(self.git_model.revision, safe='')}&per_page=20",
                timeout=config["requests"]["timeout"],
            )
        else:
            response = requests.get(
                f"{self.git_instance.api_url}/repos{project_id}/actions/runs?branch={parse.quote(self.git_model.revision, safe='')}&per_page=20",
                headers=self.get_headers(self.git_model.password),
                timeout=config["requests"]["timeout"],
            )
        response.raise_for_status()
        return response.json()["workflow_runs"]

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
        ).encode()

    def get_artifact_from_job_as_json(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> dict:
        return json.loads(
            self.get_artifact_from_job(
                project_id,
                job_id,
                trusted_path_to_artifact,
            )
        )

    def get_artifact_from_job(
        self,
        project_id: str,
        job_id: str,
        trusted_path_to_artifact: str,
    ) -> str:
        response = requests.get(
            f"{self.git_instance.api_url}/repos{project_id}/actions/runs/{job_id}/artifacts",
            headers=self.get_headers(self.git_model.password),
            timeout=config["requests"]["timeout"],
        )
        response.raise_for_status()
        artifact_id = response.json()["artifacts"][0]["id"]

        if response.json()["artifacts"][0]["expired"] == "true":
            raise fastapi.HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "err_code": "ARTIFACT_EXPIRED",
                    "reason": (
                        "The latest artifact you are requesting expired. Please rerun your pipline and contact your administrator."
                    ),
                },
            )
        artifact_response = requests.get(
            f"{self.git_instance.api_url}/repos{project_id}/actions/artifacts/{artifact_id}/zip",
            headers=self.get_headers(self.git_model.password),
            timeout=config["requests"]["timeout"],
        )
        artifact_response.raise_for_status()

        return self.get_file_content(
            artifact_response, trusted_path_to_artifact
        )

    def get_file_content(
        self, response: requests.Response, trusted_file_path: str
    ) -> str:
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            file_list = zip_file.namelist()
            file_index = file_list.index(trusted_file_path.split("/")[-1])

            with zip_file.open(file_list[file_index], "r") as file:
                return file.read().decode()

    async def get_file_from_repository(
        self,
        trusted_file_path: str,
    ) -> bytes:
        """
        If a repository is public but the permissions are not set correctly, you might be able to download the file without authentication
        but get an error when trying to load it authenticated.

        For that purpose first we try to reach it without authentication and only if that fails try to get the file authenticated.
        """
        self.check_git_instance_has_api_url()
        project_id = await self.get_project_id_by_git_url()
        response = requests.get(
            f"{self.git_instance.api_url}/repos{project_id}/contents/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(self.git_model.revision, safe='')}",
            timeout=config["requests"]["timeout"],
        )

        if not response.ok and self.git_model.password:
            response = requests.get(
                f"{self.git_instance.api_url}/repos{project_id}/contents/{parse.quote(trusted_file_path, safe='')}?ref={parse.quote(self.git_model.revision, safe='')}",
                headers=self.get_headers(self.git_model.password),
                timeout=config["requests"]["timeout"],
            )

        if response.status_code == 404:
            raise exceptions.GitRepositoryFileNotFoundError(
                filename=trusted_file_path
            )
        response.raise_for_status()
        return base64.b64decode(response.json()["content"])
