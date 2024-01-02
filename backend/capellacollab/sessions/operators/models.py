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


@dataclasses.dataclass
class PersistentVolume(Volume):
    """An persistent volume that is mounted into the container."""

    volume_name: str


class EmptyVolume(Volume):
    """An empty volume without content that is mounted into the container."""
