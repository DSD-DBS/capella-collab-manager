# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

from capellacollab.core import database


class GitValkeyCache:
    def __init__(self, git_model_id: int) -> None:
        self._valkey = database.get_valkey()
        self.git_model_id = git_model_id
        super().__init__()

    def get_file_data(
        self, file_path: str, revision: str
    ) -> tuple[datetime.datetime, bytes] | None:
        file_data = self._valkey.hmget(
            name=self._get_file_key(file_path, revision),
            keys=["last_updated", "content"],
        )
        if (last_update := file_data[0]) and (content := file_data[1]):
            last_update = datetime.datetime.fromisoformat(last_update)
            return last_update, content

        return None

    def get_artifact_data(
        self, job_id: str | int, file_path: str
    ) -> tuple[datetime.datetime, bytes] | None:
        artifact_data = self._valkey.hmget(
            name=self._get_artifact_key(job_id, file_path),
            keys=["started_at", "content"],
        )
        if (started_at := artifact_data[0]) and (content := artifact_data[1]):
            started_at = datetime.datetime.fromisoformat(started_at)
            return started_at, content

        return None

    def put_file_data(
        self,
        file_path: str,
        last_updated: datetime.datetime,
        content: bytes,
        revision: str,
        ttl: int = 3600,
    ) -> None:
        self._valkey.hset(
            name=self._get_file_key(file_path, revision),
            mapping={
                "last_updated": last_updated.isoformat(),
                "content": content,
            },
        )
        self._valkey.expire(
            name=self._get_file_key(file_path, revision), time=ttl
        )

    def put_artifact_data(
        self,
        job_id: str | int,
        file_path: str,
        started_at: datetime.datetime,
        content: bytes,
        ttl: int = 3600,
    ) -> None:
        self._valkey.hset(
            name=self._get_artifact_key(job_id, file_path),
            mapping={"started_at": started_at.isoformat(), "content": content},
        )
        self._valkey.expire(
            name=self._get_artifact_key(job_id, file_path), time=ttl
        )

    def clear(self) -> None:
        for key in self._valkey.scan_iter(match=f"{self.git_model_id}:*"):
            self._valkey.delete(key)

    def _get_file_key(self, file_path: str, revision: str) -> str:
        return f"{self.git_model_id}:f:{self._escape_string(revision)}:{self._escape_string(file_path)}"

    def _get_artifact_key(self, job_id: str | int, file_path: str) -> str:
        return (
            f"{self.git_model_id}:a:{job_id}:{self._escape_string(file_path)}"
        )

    def _escape_string(self, string: str) -> str:
        return string.replace(":", "-")
