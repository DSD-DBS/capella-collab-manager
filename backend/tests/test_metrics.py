# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import testclient

from capellacollab.sessions import metrics


def test_metrics_endpoint(client: testclient.TestClient):

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "# HELP " in response.text


def test_database_sessions_metric(db):
    collector = metrics.DatabaseSessionsCollector()

    data = list(collector.collect())

    assert data
    assert data[0].samples
