# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest

from capellacollab.sessions import models as sessions_models
from capellacollab.sessions.hooks import interface as hooks_interface
from capellacollab.sessions.hooks import log_collector
from capellacollab.sessions.operators import k8s


def test_log_volume_mounting_loki_disabled(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    post_session_creation_hook_request: hooks_interface.PostSessionCreationHookRequest,
    pre_session_termination_hook_request: hooks_interface.PreSessionTerminationHookRequest,
):
    configuration_hook_request.tool.config.monitoring.logging.enabled = False
    post_session_creation_hook_request.db_session.tool.config.monitoring.logging.enabled = False
    pre_session_termination_hook_request.session.tool.config.monitoring.logging.enabled = False
    assert (
        log_collector.LogCollectorIntegration().configuration_hook(
            configuration_hook_request
        )
        == hooks_interface.ConfigurationHookResult()
    )
    assert (
        log_collector.LogCollectorIntegration().post_session_creation_hook(
            post_session_creation_hook_request
        )
        == hooks_interface.PostSessionCreationHookResult()
    )
    assert (
        log_collector.LogCollectorIntegration().pre_session_termination_hook(
            pre_session_termination_hook_request
        )
        == hooks_interface.PreSessionTerminationHookResult()
    )


def test_log_volume_mounting(
    configuration_hook_request: hooks_interface.ConfigurationHookRequest,
    post_session_creation_hook_request: hooks_interface.PostSessionCreationHookRequest,
    pre_session_termination_hook_request: hooks_interface.PreSessionTerminationHookRequest,
    session: sessions_models.DatabaseSession,
    monkeypatch: pytest.MonkeyPatch,
):
    result = log_collector.LogCollectorIntegration().configuration_hook(
        configuration_hook_request
    )
    assert len(result["volumes"]) == 1
    assert (
        result["volumes"][0].sub_path == configuration_hook_request.session_id
    )

    create_config_map_called = 0

    def mock_create_config_map(*args, **kwargs):
        nonlocal create_config_map_called
        create_config_map_called += 1

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "create_config_map",
        mock_create_config_map,
    )

    create_sidecar_pod_called = 0

    def mock_create_sidecar_pod_called(*args, **kwargs):
        nonlocal create_sidecar_pod_called
        create_sidecar_pod_called += 1

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "create_sidecar_pod",
        mock_create_sidecar_pod_called,
    )

    log_collector.LogCollectorIntegration().post_session_creation_hook(
        post_session_creation_hook_request
    )

    assert create_config_map_called == 1
    assert create_sidecar_pod_called == 1

    delete_configmap_called = 0

    def mock_delete_configmap(*args, **kwargs):
        nonlocal delete_configmap_called
        delete_configmap_called += 1

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "delete_config_map",
        mock_delete_configmap,
    )

    delete_pod_called = 0

    def mock_delete_pod(*args, **kwargs):
        nonlocal delete_pod_called
        delete_pod_called += 1

    monkeypatch.setattr(
        k8s.KubernetesOperator,
        "delete_pod",
        mock_delete_pod,
    )

    log_collector.LogCollectorIntegration().pre_session_termination_hook(
        pre_session_termination_hook_request
    )

    assert delete_configmap_called == 1
    assert delete_pod_called == 1
