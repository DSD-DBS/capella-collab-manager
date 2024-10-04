# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("admin")
def test_create_tool_version(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
):
    """Test creating a tool version"""
    response = client.post(
        f"/api/v1/tools/{tool.id}/versions",
        json={
            "name": "test",
            "config": {
                "is_recommended": False,
                "is_deprecated": False,
                "sessions": {
                    "persistent": {"image": "docker.io/hello-world:latest"},
                    "read_only": {"image": "docker.io/hello-world:latest"},
                },
                "backups": {"image": "docker.io/hello-world:latest"},
            },
        },
    )

    assert "id" in response.json()
    assert response.is_success


@pytest.mark.usefixtures("admin")
def test_get_tools_version(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test get a tool version"""
    response = client.get(
        f"/api/v1/tools/{tool.id}/versions/{tool_version.id}",
    )

    assert response.is_success
    assert "id" in response.json()


@pytest.mark.usefixtures("admin", "tool_version")
def test_get_tools_versions(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
):
    """Test get all tool versions"""
    response = client.get(
        f"/api/v1/tools/{tool.id}/versions",
    )

    assert response.is_success
    assert len(response.json()) == 1
    assert "id" in response.json()[0]


@pytest.mark.usefixtures("admin")
def test_update_tools_version(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test updating a tool version"""
    response = client.put(
        f"/api/v1/tools/{tool.id}/versions/{tool_version.id}",
        json={
            "name": "test",
            "config": {
                "is_recommended": False,
                "is_deprecated": False,
                "sessions": {
                    "persistent": {"image": "docker.io/hello-world:latest"},
                    "read_only": {"image": "docker.io/hello-world:latest"},
                },
                "backups": {"image": "docker.io/hello-world:latest"},
            },
        },
    )

    assert response.is_success
    assert "id" in response.json()


@pytest.mark.usefixtures("user")
def test_get_tool_versions(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    response = client.get(
        f"/api/v1/tools/{tool.id}/versions",
    )

    assert response.is_success
    assert response.json()[-1]["id"] == tool_version.id


@pytest.mark.usefixtures("user")
def test_get_all_tool_versions(
    client: testclient.TestClient,
    tool_version: tools_models.DatabaseVersion,
):
    response = client.get(
        "/api/v1/tools/*/versions",
    )

    assert response.is_success
    assert response.json()[-1]["id"] == tool_version.id


@pytest.mark.usefixtures("admin")
def test_delete_tool_version(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test deleting a tool version"""
    response = client.delete(
        f"/api/v1/tools/{tool.id}/versions/{tool_version.id}",
    )

    assert response.is_success
