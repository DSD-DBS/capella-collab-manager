# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import kubernetes.client
import pytest

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions import operators
from capellacollab.sessions.hooks import networking as networking_hook
from capellacollab.users import models as users_models


def test_network_policy_created(
    user: users_models.DatabaseUser, monkeypatch: pytest.MonkeyPatch
):
    network_policy_counter = 0

    def mock_create_namespaced_network_policy(
        self,
        namespace: str,
        network_policy: kubernetes.client.V1PersistentVolumeClaim,
    ):
        nonlocal network_policy_counter
        network_policy_counter += 1

    monkeypatch.setattr(
        kubernetes.client.NetworkingV1Api,
        "create_namespaced_network_policy",
        mock_create_namespaced_network_policy,
    )

    networking_hook.NetworkingIntegration().post_session_creation_hook(
        session_id="test",
        operator=operators.KubernetesOperator(),
        user=user,
    )

    assert network_policy_counter == 1


def test_network_policy_deleted(
    session: sessions_models.DatabaseSession, monkeypatch: pytest.MonkeyPatch
):
    network_policy_del_counter = 0

    def mock_delete_namespaced_network_policy(
        self,
        name: str,
        namespace: str,
    ):
        nonlocal network_policy_del_counter
        network_policy_del_counter += 1

    monkeypatch.setattr(
        kubernetes.client.NetworkingV1Api,
        "delete_namespaced_network_policy",
        mock_delete_namespaced_network_policy,
    )

    networking_hook.NetworkingIntegration().pre_session_termination_hook(
        operator=operators.KubernetesOperator(),
        session=session,
    )

    assert network_policy_del_counter == 1
