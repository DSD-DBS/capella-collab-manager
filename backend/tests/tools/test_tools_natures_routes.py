# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("admin")
def test_create_tool_nature(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
):
    """Test creating a tool nature"""

    response = client.post(
        f"/api/v1/tools/{tool.id}/natures",
        json={
            "name": "test2",
        },
    )

    assert "id" in response.json()
    assert response.is_success
    assert response.json()["name"] == "test2"


@pytest.mark.usefixtures("admin", "tool_nature")
def test_get_tools_natures(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
):
    """Test get all tool natures"""
    response = client.get(
        f"/api/v1/tools/{tool.id}/natures",
    )

    assert response.is_success
    assert len(response.json()) == 1
    assert "id" in response.json()[0]
    assert response.json()[0]["name"] == "test"


@pytest.mark.usefixtures("admin")
def test_get_tools_nature(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_nature: tools_models.DatabaseNature,
):
    """Test get a tool nature"""
    response = client.get(
        f"/api/v1/tools/{tool.id}/natures/{tool_nature.id}",
    )

    assert "id" in response.json()
    assert response.is_success
    assert response.json()["name"] == "test"


@pytest.mark.usefixtures("admin")
def test_update_tools_nature(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_nature: tools_models.DatabaseNature,
):
    """Test updating a tool nature"""
    response = client.put(
        f"/api/v1/tools/{tool.id}/natures/{tool_nature.id}",
        json={
            "name": "test_new",
        },
    )

    assert "id" in response.json()
    assert response.is_success
    assert response.json()["name"] == "test_new"


@pytest.mark.usefixtures("admin")
def test_delete_tool_nature(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_nature: tools_models.DatabaseNature,
):
    """Test deleting a tool nature"""
    response = client.delete(
        f"/api/v1/tools/{tool.id}/natures/{tool_nature.id}",
    )

    assert response.is_success
