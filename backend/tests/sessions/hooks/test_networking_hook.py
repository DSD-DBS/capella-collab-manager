# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import kubernetes.client
import pytest

from capellacollab.sessions.hooks import interface as session_hooks_interface
from capellacollab.sessions.hooks import networking as networking_hook


def test_network_policy_created(
    monkeypatch: pytest.MonkeyPatch,
    post_session_creation_hook_request: session_hooks_interface.PostSessionCreationHookRequest,
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
        post_session_creation_hook_request
    )

    assert network_policy_counter == 1


def test_network_policy_deleted(
    monkeypatch: pytest.MonkeyPatch,
    pre_session_termination_hook_request: session_hooks_interface.PreSessionTerminationHookRequest,
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
        pre_session_termination_hook_request
    )

    assert network_policy_del_counter == 1
