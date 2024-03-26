# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from kubernetes import client as kubernetes_client
from kubernetes.client import exceptions as kubernetes_exceptions

from capellacollab.sessions.operators import k8s


def test_persistent_volume_exists(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    monkeypatch.setattr(
        operator.v1_core,
        "read_namespaced_persistent_volume_claim",
        lambda name, namespace: None,
    )

    assert operator.persistent_volume_exists("test") is True


def test_persistent_volume_doesnt_exists(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    def mock_read_namespaced_persistent_volume_claim(name, namespace):
        raise kubernetes_exceptions.ApiException(status=404)

    monkeypatch.setattr(
        operator.v1_core,
        "read_namespaced_persistent_volume_claim",
        mock_read_namespaced_persistent_volume_claim,
    )

    assert operator.persistent_volume_exists("test") is False


def test_persistent_volume_exists_error(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    def mock_read_namespaced_persistent_volume_claim(name, namespace):
        raise kubernetes_exceptions.ApiException(status=500)

    monkeypatch.setattr(
        operator.v1_core,
        "read_namespaced_persistent_volume_claim",
        mock_read_namespaced_persistent_volume_claim,
    )

    with pytest.raises(kubernetes_exceptions.ApiException):
        operator.persistent_volume_exists("test")


def test_create_persistent_volume(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    monkeypatch.setattr(
        operator.v1_core,
        "create_namespaced_persistent_volume_claim",
        lambda namespace, pvc: None,
    )

    operator.create_persistent_volume("test", "10Gi", {})


def test_create_persistent_volume_already_exists(
    monkeypatch: pytest.MonkeyPatch,
):
    operator = k8s.KubernetesOperator()

    def mock_create_namespaced_persistent_volume_claim(name, namespace):
        raise kubernetes_exceptions.ApiException(status=409)

    monkeypatch.setattr(
        operator.v1_core,
        "create_namespaced_persistent_volume_claim",
        mock_create_namespaced_persistent_volume_claim,
    )

    operator.create_persistent_volume("test", "10Gi", {})


def test_create_persistent_volume_error(
    monkeypatch: pytest.MonkeyPatch,
):
    operator = k8s.KubernetesOperator()

    def mock_create_namespaced_persistent_volume_claim(name, namespace):
        raise kubernetes_exceptions.ApiException(status=500)

    monkeypatch.setattr(
        operator.v1_core,
        "create_namespaced_persistent_volume_claim",
        mock_create_namespaced_persistent_volume_claim,
    )

    with pytest.raises(kubernetes_exceptions.ApiException):
        operator.create_persistent_volume("test", "10Gi", {})


def test_delete_persistent_volume(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()
    monkeypatch.setattr(
        operator.v1_core,
        "delete_namespaced_persistent_volume_claim",
        lambda name, namespace: kubernetes_client.V1Status(),
    )

    operator.delete_persistent_volume("test")


def test_delete_persistent_volume_not_found(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    def mock_delete_namespaced_persistent_volume_claim(name, namespace):
        raise kubernetes_exceptions.ApiException(status=404)

    monkeypatch.setattr(
        operator.v1_core,
        "delete_namespaced_persistent_volume_claim",
        mock_delete_namespaced_persistent_volume_claim,
    )

    operator.delete_persistent_volume("test")


def test_delete_persistent_volume_error(monkeypatch: pytest.MonkeyPatch):
    operator = k8s.KubernetesOperator()

    def mock_delete_namespaced_persistent_volume_claim(name, namespace):
        raise kubernetes_exceptions.ApiException(status=500)

    monkeypatch.setattr(
        operator.v1_core,
        "delete_namespaced_persistent_volume_claim",
        mock_delete_namespaced_persistent_volume_claim,
    )

    with pytest.raises(kubernetes_exceptions.ApiException):
        operator.delete_persistent_volume("test")
