# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from kubernetes import client
from kubernetes.client import exceptions as kubernetes_exceptions

from capellacollab import core
from capellacollab.sessions import injection
from capellacollab.sessions.operators import k8s


def test_get_last_seen_disabled_in_development_mode(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(core, "LOCAL_DEVELOPMENT_MODE", True)
    assert injection.get_last_seen("test") == "Disabled in development mode"


def test_started_session_state(monkeypatch: pytest.MonkeyPatch):
    """Test the session state with the following conditions:

    - The session preparation is finished.
    - The session container is started, but the logs are not yet available.

    The expected result is "FINISH_PREPARE_WORKSPACE".
    """

    def mock_list_namespaced_pod(
        self, namespace: str, label_selector: str
    ) -> client.V1PodList:
        return client.V1PodList(
            items=[
                client.V1Pod(
                    metadata=client.V1ObjectMeta(name="test"),
                )
            ]
        )

    def mock_list_namespaced_event(
        self, namespace: str, field_selector: str
    ) -> client.V1PodList:
        return client.CoreV1EventList(
            items=[
                client.CoreV1Event(
                    metadata=client.V1ObjectMeta(name="test"),
                    involved_object=client.V1ObjectReference(name="test"),
                    reason="Started",
                )
            ]
        )

    def mock_read_namespaced_pod_log(
        self, name: str, container: str, namespace: str
    ) -> str:
        if container == "session-preparation":
            return "---FINISH_PREPARE_WORKSPACE---"

        # Finished session preparation, but container hasn't started yet.
        raise kubernetes_exceptions.ApiException(status=400)

    monkeypatch.setattr(
        client.CoreV1Api,
        "list_namespaced_event",
        mock_list_namespaced_event,
    )

    monkeypatch.setattr(
        client.CoreV1Api,
        "list_namespaced_pod",
        mock_list_namespaced_pod,
    )

    monkeypatch.setattr(
        client.CoreV1Api,
        "read_namespaced_pod_log",
        mock_read_namespaced_pod_log,
    )

    assert "FINISH_PREPARE_WORKSPACE" == injection.determine_session_state(
        "test"
    )
