# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient

from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("admin")
def test_create_tool_version(
    client: testclient.TestClient, tool: tools_models.DatabaseTool
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
                "configuration": {
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
