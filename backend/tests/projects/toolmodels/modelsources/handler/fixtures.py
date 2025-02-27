# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import logging

import pytest

import capellacollab.settings.modelsources.git.models as git_models
import capellacollab.settings.modelsources.t4c.instance.models as t4c_models
import capellacollab.settings.modelsources.t4c.instance.repositories.interface as t4c_repositories_interface
from capellacollab.core import credentials


@pytest.fixture(name="mock_git_valkey_cache")
def fixture_mock_git_valkey_cache(monkeypatch: pytest.MonkeyPatch):
    class MockGitValkeyCache:
        cache: dict[str, tuple[datetime.datetime, bytes]] = {}

        def __init__(self, *args, **kwargs) -> None:
            super().__init__()

        async def get_file_data(
            self,
            file_path: str,
            revision: str,
            logger: logging.LoggerAdapter,
        ) -> tuple[datetime.datetime, bytes] | None:
            return MockGitValkeyCache.cache.get(f"f:{file_path}", None)

        async def get_artifact_data(
            self,
            job_id: str,
            file_path: str,
            logger: logging.LoggerAdapter,
        ) -> tuple[datetime.datetime, bytes] | None:
            return MockGitValkeyCache.cache.get(f"a:{file_path}:{job_id}")

        async def put_file_data(
            self,
            file_path: str,
            last_updated: datetime.datetime,
            content: bytes,
            revision: str,
            logger: logging.LoggerAdapter,
        ) -> None:
            MockGitValkeyCache.cache[f"f:{file_path}"] = (
                last_updated,
                content,
            )

        async def put_artifact_data(
            self,
            job_id: str,
            file_path: str,
            started_at: datetime.datetime,
            content: bytes,
            logger: logging.LoggerAdapter,
        ) -> None:
            MockGitValkeyCache.cache[f"a:{file_path}:{job_id}"] = (
                started_at,
                content,
            )

        async def clear(self) -> None:
            MockGitValkeyCache.cache.clear()

    monkeypatch.setattr(
        "capellacollab.projects.toolmodels.modelsources.git.handler.cache.GitValkeyCache",
        MockGitValkeyCache,
    )

    return MockGitValkeyCache()


@pytest.fixture(
    name="git_type",
    params=[git_models.GitType.GITLAB, git_models.GitType.GITHUB],
)
def fixture_git_type(request: pytest.FixtureRequest) -> git_models.GitType:
    return request.param


@pytest.fixture(name="mock_add_user_to_t4c_repository")
def fixture_mock_add_user_to_t4c_repository(monkeypatch: pytest.MonkeyPatch):
    def mock_add_user_to_repository(
        instance: t4c_models.DatabaseT4CInstance,
        repository_name: str,
        username: str,
        password: str = credentials.generate_password(),
        is_admin: bool = False,
    ):
        return {}

    monkeypatch.setattr(
        t4c_repositories_interface,
        "add_user_to_repository",
        mock_add_user_to_repository,
    )
