# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("admin")
def test_delete_tool_version_with_references(
    db: orm.Session,
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test deleting a tool version which is registered as compatible in another version

    The tool version is registered as config.compatible_versions
    """

    tool_version2 = tools_models.CreateToolVersion(
        name="test2",
        config=tools_models.ToolVersionConfiguration(),
    )
    created_tool_version2 = tools_crud.create_version(db, tool, tool_version2)

    tool_version3 = tools_models.CreateToolVersion(
        name="test3",
        config=tools_models.ToolVersionConfiguration(
            compatible_versions=[tool_version.id, created_tool_version2.id]
        ),
    )
    created_tool_version3 = tools_crud.create_version(db, tool, tool_version3)

    response = client.delete(
        f"/api/v1/tools/{tool.id}/versions/{tool_version.id}",
    )

    assert response.is_success

    # Check that tool_version id was removed from tool_version3 compatible versions
    db.refresh(created_tool_version3)
    assert created_tool_version3.config.compatible_versions == [
        created_tool_version2.id
    ]


@pytest.mark.usefixtures("admin")
def test_delete_tool_with_version_references(
    db: orm.Session,
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test deleting a tool which has a version which is registered as compatible in another version

    The tool version is registered as config.compatible_versions
    """
    test_tool = tools_models.CreateTool(name="test")
    created_test_tool = tools_crud.create_tool(db, test_tool)

    test_tool_version = tools_models.CreateToolVersion(
        name="test3",
    )
    created_test_tool_version = tools_crud.create_version(
        db, created_test_tool, test_tool_version
    )

    tool_version3 = tools_models.CreateToolVersion(
        name="test3",
        config=tools_models.ToolVersionConfiguration(
            compatible_versions=[tool_version.id, created_test_tool_version.id]
        ),
    )
    created_tool_version3 = tools_crud.create_version(db, tool, tool_version3)

    response = client.delete(
        f"/api/v1/tools/{created_test_tool.id}",
    )

    assert response.is_success

    # Check that capella_version id was removed from tool_version3 compatible versions
    db.refresh(created_tool_version3)
    assert created_tool_version3.config.compatible_versions == [
        tool_version.id
    ]


@pytest.mark.usefixtures("admin")
def test_update_tool_version_with_own_reference(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test to update a tool as self-compatible"""

    response = client.put(
        f"/api/v1/tools/{tool.id}/versions/{tool_version.id}",
        json={
            "name": "test",
            "config": {
                "compatible_versions": [tool_version.id],
            },
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "COMPATIBLE_TOOL_VERSION_CANT_REFERENCE_OWN_TOOL_VERSION"
    )


@pytest.mark.usefixtures("admin")
def test_update_tool_version_with_non_existing_reference(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
    tool_version: tools_models.DatabaseVersion,
):
    """Test to update with a non-existing compatible tool"""

    response = client.put(
        f"/api/v1/tools/{tool.id}/versions/{tool_version.id}",
        json={
            "name": "test",
            "config": {
                "compatible_versions": [-1],
            },
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "COMPATIBLE_TOOL_VERSION_NOT_FOUND"
    )


@pytest.mark.usefixtures("admin")
def test_create_tool_version_with_non_existing_reference(
    client: testclient.TestClient,
    tool: tools_models.DatabaseTool,
):
    """Test to create with a non-existing compatible tool"""

    response = client.post(
        f"/api/v1/tools/{tool.id}/versions",
        json={
            "name": "test",
            "config": {
                "compatible_versions": [-1],
            },
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "COMPATIBLE_TOOL_VERSION_NOT_FOUND"
    )
