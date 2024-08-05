# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime

from capellacollab.core import database


class GitRedisCache:
    def __init__(self, path: str, revision: str) -> None:
        self._redis = database.get_redis()
        self.path = path.replace(":", "-")
        self.revision = revision
        super().__init__()

    def get_file_data(
        self, file_path: str, revision: str | None = None
    ) -> tuple[datetime.datetime, bytes] | None:
        revision = revision or self.revision

        file_data = self._redis.hmget(
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
        artifact_data = self._redis.hmget(
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
        revision: str | None = None,
        ttl: int = 3600,
    ) -> None:
        revision = revision or self.revision

        self._redis.hset(
            name=self._get_file_key(file_path, revision),
            mapping={
                "last_updated": last_updated.isoformat(),
                "content": content,
            },
        )
        self._redis.expire(
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
        self._redis.hset(
            name=self._get_artifact_key(job_id, file_path),
            mapping={"started_at": started_at.isoformat(), "content": content},
        )
        self._redis.expire(
            name=self._get_artifact_key(job_id, file_path), time=ttl
        )

    def clear(self, ignore_revision: bool = False) -> None:
        pattern = f"{self.path}:{self.revision}:*"
        if ignore_revision:
            pattern = f"{self.path}:*"

        for key in self._redis.scan_iter(match=pattern):
            self._redis.delete(key)

    def _get_file_key(self, file_path: str, revision: str) -> str:
        file_path = file_path.replace(":", "-")
        return f"{self.path}:{revision}:f:{file_path}"

    def _get_artifact_key(self, job_id: str | int, file_path: str) -> str:
        file_path = file_path.replace(":", "-")
        return f"{self.path}:{self.revision}:a:{job_id}:{file_path}"
