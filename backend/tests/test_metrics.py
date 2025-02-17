# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from kubernetes import client as k8s_client

from capellacollab.sessions import metrics


def test_metrics_endpoint(client_unauthenticated: testclient.TestClient):
    response = client_unauthenticated.get("/metrics")

    assert response.status_code == 200
    assert "# HELP " in response.text


def test_database_sessions_metric_empty():
    collector = metrics.DatabaseSessionsCollector()

    data = list(collector.collect())

    assert data
    assert data[0].samples


def test_kubernetes_sessions_metric(monkeypatch: pytest.MonkeyPatch):
    def mock_list_namespaced_pod(
        self,
        namespace: str,
        label_selector: str,
    ) -> k8s_client.V1PodList:
        return k8s_client.V1PodList(
            items=[
                k8s_client.V1Pod(
                    metadata=k8s_client.V1ObjectMeta(),
                    status=k8s_client.V1PodStatus(phase="running"),
                ),
                k8s_client.V1Pod(
                    metadata=k8s_client.V1ObjectMeta(
                        labels={"workload": "job"}
                    ),
                    status=k8s_client.V1PodStatus(phase="pending"),
                ),
                k8s_client.V1Pod(
                    metadata=k8s_client.V1ObjectMeta(
                        labels={"workload": "job"}
                    ),
                    status=k8s_client.V1PodStatus(phase="running"),
                ),
                k8s_client.V1Pod(
                    metadata=k8s_client.V1ObjectMeta(
                        labels={"workload": "session"}
                    ),
                    status=k8s_client.V1PodStatus(phase="running"),
                ),
                k8s_client.V1Pod(
                    metadata=k8s_client.V1ObjectMeta(
                        labels={"workload": "session"}
                    ),
                    status=k8s_client.V1PodStatus(phase="running"),
                ),
            ]
        )

    monkeypatch.setattr(
        k8s_client.CoreV1Api,
        "list_namespaced_pod",
        mock_list_namespaced_pod,
    )

    collector = metrics.DeployedSessionsCollector()
    data = list(collector.collect())

    samples = {
        (s.labels["workload"], s.labels["phase"]): s.value
        for s in data[0].samples
    }

    assert samples == {
        ("job", "running"): 1,
        ("job", "pending"): 1,
        ("session", "running"): 2,
    }
