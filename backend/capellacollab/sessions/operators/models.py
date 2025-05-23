# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc
import dataclasses
import pathlib


@dataclasses.dataclass
class Volume(metaclass=abc.ABCMeta):
    name: str
    read_only: bool
    container_path: pathlib.PurePosixPath
    sub_path: str | None


@dataclasses.dataclass
class SecretReferenceVolume(Volume):
    """Mount an existing secret to the container."""

    secret_name: str
    optional: bool


@dataclasses.dataclass
class ConfigMapReferenceVolume(Volume):
    """Mount an existing config map volume to the container."""

    config_map_name: str
    optional: bool


@dataclasses.dataclass
class PersistentVolume(Volume):
    """A persistent volume that is mounted into the container."""

    volume_name: str


class EmptyVolume(Volume):
    """An empty volume without content that is mounted into the container."""
