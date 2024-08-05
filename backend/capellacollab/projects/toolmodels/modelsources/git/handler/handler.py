# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import abc
import datetime
import json
import typing as t

import requests

from capellacollab.core import cache

from .. import exceptions

if t.TYPE_CHECKING:
    from capellambse import diagram_cache


class GitHandler:
    cache: cache.Cache = cache.InMemoryCache()

    def __init__(
        self,
        path: str,
        revision: str,
        password: str,
        api_url: str,
        project_id: str,
    ) -> None:
        self.path = path
        self.revision = revision
        self.password = password
        self.api_url = api_url
        self.project_id = project_id

    @classmethod
    @abc.abstractmethod
    async def get_project_id_by_git_url(
        cls, path: str, password: str, api_url: str
    ) -> str:
        pass

    @abc.abstractmethod
    async def get_last_job_run_id(self, job_name: str) -> tuple[str, str]:
        pass

    @abc.abstractmethod
    def get_artifact_from_job_as_content(
        self, job_id: str, trusted_path_to_artifact: str
    ) -> bytes:
        pass

    @abc.abstractmethod
    def get_file_from_repository(
        self, trusted_file_path: str, revision: str | None = None
    ) -> bytes:
        pass

    @abc.abstractmethod
    def get_last_updated_for_file_path(
        self, file_path: str, revision: str | None
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
        try:
            f_last_updated = self.get_last_updated_for_file_path(
                trusted_file_path, revision
            )

            f_content = self._get_content_from_cache(
                trusted_file_path, "file", revision
            )

            if not f_content:
                f_content = self.get_file_from_repository(
                    trusted_file_path, revision
                )
                self._store_content_in_cache(
                    trusted_file_path, f_content, "file", revision
                )
            return (f_last_updated, f_content)
        except (requests.HTTPError, exceptions.GitRepositoryFileNotFoundError):
            pass

        job_id, a_last_updated = await self.get_last_job_run_id(job_name)

        a_content = self._get_content_from_cache(
            f"{job_id}-{trusted_file_path}", "artifact", revision
        )
        if not a_content:
            a_content = self.get_artifact_from_job_as_content(
                job_id, trusted_file_path
            )
            self._store_content_in_cache(
                f"{job_id}-{trusted_file_path}",
                a_content,
                "artifact",
                revision,
            )

        return (a_last_updated, a_content)

    def _get_content_from_cache(
        self, content_id: str, prefix: str, revision: str | None = None
    ) -> bytes | None:
        revision = revision if revision else self.revision

        key = f"{prefix}-{self.project_id}-{content_id}-{revision}"

        return GitHandler.cache.get(key)

    def _store_content_in_cache(
        self,
        content_id: str,
        content: bytes,
        prefix: str,
        revision: str | None = None,
    ) -> None:
        revision = revision if revision else self.revision

        key = f"{prefix}-{self.project_id}-{content_id}-{revision}"

        GitHandler.cache.set(key, content)
