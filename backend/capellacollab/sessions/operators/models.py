# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import abc
import dataclasses
import pathlib
import typing as t


@dataclasses.dataclass
class Volume(metaclass=abc.ABCMeta):
    name: str
    read_only: bool
    container_path: pathlib.PurePosixPath


@dataclasses.dataclass
class ConfigurationVolume(Volume):
    """A configuration file that is mounted to the container."""

    file_name: str
    content: str


@dataclasses.dataclass
class SecretReferenceVolume(Volume):
    """Mount an existing secret to the container."""

    secret_name: str
    optional: bool


@dataclasses.dataclass
class PersistentVolume(Volume):
    """An persistent volume that is mounted into the container."""

    volume_name: str


class EmptyVolume(Volume):
    """An empty volume without content that is mounted into the container."""


@dataclasses.dataclass
class Container:
    image: str
    entrypoint: list[str]
    volumes: list[Volume]
    environment: t.Mapping
