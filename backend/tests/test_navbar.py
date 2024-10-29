# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

from capellacollab import core


@pytest.fixture(name="cluster_development_mode")
def fixture_cluster_development_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(core, "CLUSTER_DEVELOPMENT_MODE", True)
    monkeypatch.setattr(core, "DEVELOPMENT_MODE", True)


@pytest.fixture(name="local_development_mode")
def fixture_local_development_mode(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(core, "LOCAL_DEVELOPMENT_MODE", True)
    monkeypatch.setattr(core, "DEVELOPMENT_MODE", True)


@pytest.mark.usefixtures("admin", "cluster_development_mode")
def test_cluster_dev_mode(
    client: testclient.TestClient,
):
    client.put(
        "/api/v1/configurations/global",
        json={
            "navbar": {
                "badge": {"text": "auto", "variant": "auto", "show": True}
            }
        },
    )
    response = client.get("/api/v1/configurations/unified")
    assert response.status_code == 200
    assert response.json()["navbar"]["badge"]["text"] == "Cluster Development"
    assert response.json()["navbar"]["badge"]["variant"] == "warning"


@pytest.mark.usefixtures(
    "admin",
    "local_development_mode",
)
def test_local_dev_mode(
    client: testclient.TestClient,
):
    client.put(
        "/api/v1/configurations/global",
        json={
            "navbar": {
                "badge": {"text": "auto", "variant": "auto", "show": True}
            }
        },
    )
    response = client.get("/api/v1/configurations/unified")
    assert response.status_code == 200
    assert response.json()["navbar"]["badge"]["text"] == "Local Development"
    assert response.json()["navbar"]["badge"]["variant"] == "warning"


@pytest.mark.usefixtures("admin")
def test_fallback_env_mode(client: testclient.TestClient):
    response = client.put(
        "/api/v1/configurations/global",
        json={
            "metadata": {
                "environment": "Fallback Environment",
            },
            "navbar": {
                "badge": {"text": "auto", "variant": "auto", "show": True}
            },
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/configurations/unified")
    assert response.status_code == 200
    assert response.json()["navbar"]["badge"]["text"] == "Fallback Environment"
    assert response.json()["navbar"]["badge"]["variant"] == "success"


@pytest.mark.usefixtures("admin")
def test_unknown_env_mode(
    client: testclient.TestClient,
):
    response = client.put(
        "/api/v1/configurations/global",
        json={
            "metadata": {
                "environment": "",
            },
            "navbar": {
                "badge": {"text": "auto", "variant": "auto", "show": True}
            },
        },
    )

    assert response.status_code == 200

    response = client.get("/api/v1/configurations/unified")
    assert response.status_code == 200
    assert response.json()["navbar"]["badge"]["text"] == "Unknown Environment"
    assert response.json()["navbar"]["badge"]["variant"] == "warning"
