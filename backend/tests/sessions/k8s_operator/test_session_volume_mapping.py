# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pathlib

import pytest

from capellacollab.sessions.operators import k8s
from capellacollab.sessions.operators import models as operators_models


def test_secret_reference_volume_mapping():
    operator = k8s.KubernetesOperator()

    volumes: list[operators_models.Volume] = [
        operators_models.SecretReferenceVolume(
            name="test",
            read_only=True,
            container_path=pathlib.PurePosixPath("/inputs/test"),
            secret_name="test",
            optional=True,
            sub_path=None,
        )
    ]

    k8s_volumes, k8s_volume_mounts = operator._map_volumes_to_k8s_volumes(
        volumes
    )

    assert len(k8s_volumes) == 1
    assert len(k8s_volume_mounts) == 1

    assert k8s_volumes[0].name == "test"
    assert k8s_volumes[0].secret.secret_name == "test"
    assert k8s_volumes[0].secret.optional is True

    assert k8s_volume_mounts[0].name == "test"
    assert k8s_volume_mounts[0].mount_path == "/inputs/test"
    assert k8s_volume_mounts[0].read_only is True


def test_persistent_volume_mapping():
    operator = k8s.KubernetesOperator()

    volumes: list[operators_models.Volume] = [
        operators_models.PersistentVolume(
            name="test",
            read_only=True,
            container_path=pathlib.PurePosixPath("/inputs/test"),
            volume_name="volume_test",
            sub_path=None,
        )
    ]

    k8s_volumes, k8s_volume_mounts = operator._map_volumes_to_k8s_volumes(
        volumes
    )

    assert len(k8s_volumes) == 1
    assert len(k8s_volume_mounts) == 1

    assert k8s_volumes[0].name == "test"
    assert k8s_volumes[0].persistent_volume_claim.claim_name == "volume_test"

    assert k8s_volume_mounts[0].name == "test"
    assert k8s_volume_mounts[0].mount_path == "/inputs/test"
    assert k8s_volume_mounts[0].read_only is True


def test_empty_volume_mapping():
    operator = k8s.KubernetesOperator()

    volumes: list[operators_models.Volume] = [
        operators_models.EmptyVolume(
            name="test",
            read_only=True,
            container_path=pathlib.PurePosixPath("/inputs/test"),
            sub_path=None,
        )
    ]

    k8s_volumes, k8s_volume_mounts = operator._map_volumes_to_k8s_volumes(
        volumes
    )

    assert len(k8s_volumes) == 1
    assert len(k8s_volume_mounts) == 1

    assert k8s_volumes[0].name == "test"
    assert k8s_volumes[0].empty_dir

    assert k8s_volume_mounts[0].name == "test"
    assert k8s_volume_mounts[0].mount_path == "/inputs/test"
    assert k8s_volume_mounts[0].read_only is True


def test_invalid_volume_mapping():
    operator = k8s.KubernetesOperator()

    class RandomVolume(operators_models.Volume):
        pass

    volumes: list[operators_models.Volume] = [
        RandomVolume(
            name="test",
            read_only=True,
            container_path=pathlib.PurePosixPath("/inputs/test"),
            sub_path=None,
        )
    ]

    with pytest.raises(KeyError):
        _ = operator._map_volumes_to_k8s_volumes(volumes)
