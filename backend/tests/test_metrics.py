# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import testclient

from capellacollab.sessions import metrics, operators


def test_metrics_endpoint(client: testclient.TestClient):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "# HELP " in response.text


def test_database_sessions_metric(db):
    collector = metrics.DatabaseSessionsCollector()

    data = list(collector.collect())

    assert data
    assert data[0].samples


def test_kubernetes_sessions_metric(monkeypatch):
    monkeypatch.setattr(operators, "get_operator", MockOperator)
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


class MockOperator:
    def get_pods(self, label_selector):
        return [
            attrdict(
                metadata=attrdict(labels=dict(workload="job")),
                status=attrdict(phase="running"),
            ),
            attrdict(
                metadata=attrdict(labels=dict(workload="job")),
                status=attrdict(phase="pending"),
            ),
            attrdict(
                metadata=attrdict(labels=dict(workload="session")),
                status=attrdict(phase="running"),
            ),
            attrdict(
                metadata=attrdict(labels=dict(workload="session")),
                status=attrdict(phase="running"),
            ),
        ]


class attrdict(dict):
    def __getattr__(self, name):
        return self[name]
