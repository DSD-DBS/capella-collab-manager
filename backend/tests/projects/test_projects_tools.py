# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import pytest
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.projects import models as projects_models
from capellacollab.projects.tools import crud as projects_tools_crud
from capellacollab.projects.tools import models as projects_tools_models
from capellacollab.tools import models as tools_models


@pytest.fixture(name="project_tool")
def fixture_jupyter_project_tool(
    db: orm.Session,
    project: projects_models.DatabaseProject,
    tool_version: tools_models.DatabaseVersion,
) -> projects_tools_models.DatabaseProjectToolAssociation:
    return projects_tools_crud.create_project_tool(db, project, tool_version)


@pytest.mark.usefixtures("capella_model", "project_tool", "project_user")
def test_get_project_tools(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_tool_version: tools_models.DatabaseVersion,
    tool_version: tools_models.DatabaseVersion,
):
    """Test to get all tools of a project

    Explicitly test that manually added tools
    and auto-added tools are listed.
    """

    response = client.get(f"/api/v1/projects/{project.slug}/tools")

    assert response.status_code == 200
    json = response.json()

    assert len(json) == 2
    assert json[0]["tool_version"]["id"] == tool_version.id
    assert json[1]["tool_version"]["id"] == capella_tool_version.id
    assert len(json[1]["used_by"]) == 1


@pytest.mark.usefixtures("project_manager")
def test_link_tool_to_project(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_tool_version: tools_models.DatabaseVersion,
):
    """Test to link a tool to a project"""

    response = client.post(
        f"/api/v1/projects/{project.slug}/tools",
        json={
            "tool_version_id": capella_tool_version.id,
            "tool_id": capella_tool_version.tool.id,
        },
    )

    assert response.status_code == 200
    assert response.json()["tool_version"]["id"] == capella_tool_version.id


@pytest.mark.usefixtures("project_tool", "project_manager")
def test_link_tool_to_project_already_linked(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    tool_version: tools_models.DatabaseVersion,
):
    """Test to link a tool to a project that is already linked"""
    response = client.post(
        f"/api/v1/projects/{project.slug}/tools",
        json={
            "tool_version_id": tool_version.id,
            "tool_id": tool_version.tool.id,
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"]
        == "TOOL_ALREADY_EXISTS_IN_PROJECT"
    )


@pytest.mark.usefixtures("project_manager")
def test_remove_tool_from_project(
    db: orm.Session,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    project_tool: projects_tools_models.DatabaseProjectToolAssociation,
):
    """Test to remove a tool to a project"""

    response = client.delete(
        f"/api/v1/projects/{project.slug}/tools/{project_tool.id}"
    )

    assert response.status_code == 204
    assert (
        projects_tools_crud.get_project_tool_by_id(db, project_tool.id) is None
    )


@pytest.mark.usefixtures("project_manager")
def test_remove_non_existing_tool_from_project(
    db: orm.Session,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
):
    """Test to remove a non-existing tools to a project"""

    response = client.delete(f"/api/v1/projects/{project.slug}/tools/0")

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "PROJECT_TOOL_NOT_FOUND"
