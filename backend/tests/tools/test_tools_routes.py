# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

from capellacollab.tools import models as tools_models


@pytest.fixture(name="tools_json")
def fixture_tools_json() -> dict:
    return {
        "name": "This is a test tool",
        "integrations": {
            "t4c": False,
            "pure_variants": False,
        },
        "config": {
            "resources": {
                "cpu": {"limits": 2, "requests": 0.4},
                "memory": {"limits": "6Gi", "requests": "1.6Gi"},
            },
            "connection": {
                "methods": [
                    {
                        "id": "a719b91d-a47a-4006-b774-916b01ccb58d",
                        "name": "default",
                        "ports": {"metrics": 9118, "rdp": 3389},
                        "type": "guacamole",
                    },
                ]
            },
            "monitoring": {"prometheus": {"path": "/prometheus"}},
            "supported_project_types": ["general"],
        },
    }


@pytest.mark.usefixtures("admin")
def test_create_tool(client: testclient.TestClient, tools_json: dict):
    """Test creating a tool"""

    response = client.post("/api/v1/tools", json=tools_json)

    assert response.is_success
    assert "id" in response.json()


@pytest.mark.usefixtures("admin")
def test_tool_duplicate_supported_project_types(
    client: testclient.TestClient, tools_json: dict
):
    tools_json["config"]["supported_project_types"] = ["general", "general"]
    response = client.post("/api/v1/tools", json=tools_json)

    assert response.status_code == 422


@pytest.mark.usefixtures("admin")
def test_update_tool(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tools_json: dict,
):
    """Test updating a tool"""

    tools_json["integrations"]["pure_variants"] = True
    response = client.put(f"/api/v1/tools/{tool.id}", json=tools_json)

    assert response.is_success
    assert "id" in response.json()
    assert response.json()["integrations"]["pure_variants"] is True


@pytest.mark.usefixtures("admin")
def test_delete_tool(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
):
    """Test deleting a tool"""
    response = client.delete(
        f"/api/v1/tools/{tool.id}",
    )

    assert response.is_success


@pytest.mark.usefixtures("project_manager")
def test_get_tools(client: testclient.TestClient):
    response = client.get("/api/v1/tools")
    out = response.json()

    assert response.status_code == 200
    assert "Capella" in (tool["name"] for tool in out)
