# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import testclient


def test_metrics_endpoint(client: testclient.TestClient):

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "# HELP " in response.text
