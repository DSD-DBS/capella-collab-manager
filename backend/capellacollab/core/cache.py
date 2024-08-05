# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import abc


class Cache(abc.ABC):
    @abc.abstractmethod
    def get(self, key: str) -> bytes | None:
        pass

    @abc.abstractmethod
    def set(self, key: str, value: bytes) -> None:
        pass

    @abc.abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abc.abstractmethod
    def clear(self) -> None:
        pass


class InMemoryCache(Cache):
    def __init__(self) -> None:
        self.cache: dict[str, bytes] = {}

    def get(self, key: str) -> bytes | None:
        return self.cache.get(key, None)

    def set(self, key: str, value: bytes) -> None:
        self.cache[key] = value

    def delete(self, key: str) -> None:
        self.cache.pop(key)

    def clear(self) -> None:
        self.cache.clear()
