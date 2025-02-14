# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from uuid import uuid4

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
from capellacollab.projects import crud as projects_crud
from capellacollab.projects import models as projects_models
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.tools import crud as tools_crud
from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("admin")
def test_rename_toolmodel_successful(
    capella_model: toolmodels_models.DatabaseToolModel,
    project: projects_models.DatabaseProject,
    client: testclient.TestClient,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={
            "name": "new-name",
            "version_id": capella_model.tool.versions[0].id,
            "nature_id": capella_model.tool.natures[0].id,
        },
    )

    assert response.status_code == 200
    assert "new-name" in response.text


@pytest.mark.usefixtures("admin")
def test_rename_toolmodel_where_name_already_exists(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    jupyter_model: toolmodels_models.DatabaseToolModel,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"name": jupyter_model.name, "version_id": -1, "nature_id": -1},
    )

    assert response.status_code == 409
    assert response.json()["detail"]["err_code"] == "TOOLMODEL_ALREADY_EXISTS"


@pytest.mark.usefixtures("admin")
def test_update_toolmodel_order_successful(
    capella_model: toolmodels_models.DatabaseToolModel,
    project: projects_models.DatabaseProject,
    client: testclient.TestClient,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"display_order": 1},
    )

    assert response.status_code == 200
    assert "1" in response.text


def test_move_toolmodel(
    project: projects_models.DatabaseProject,
    project_manager: projects_users_models.DatabaseProjectUserAssociation,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    db: orm.Session,
):
    second_project = projects_crud.create_project(db, str(uuid4()))
    projects_users_crud.add_user_to_project(
        db,
        project=second_project,
        user=project_manager.user,
        role=projects_users_models.ProjectUserRole.MANAGER,
        permission=projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"project_slug": second_project.slug},
    )
    assert response.status_code == 200

    response = client.get(
        f"/api/v1/projects/{second_project.slug}/models/{capella_model.slug}"
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("project_manager")
def test_move_toolmodel_non_project_member(
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.ToolModel,
    client: testclient.TestClient,
    db: orm.Session,
):
    second_project = projects_crud.create_project(db, str(uuid4()))

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}",
        json={"project_slug": second_project.slug},
    )
    assert response.status_code == 403


@pytest.mark.usefixtures("t4c_model", "project_manager")
def test_patch_toolmodel_version_with_invalid_t4c_link(
    db: orm.Session,
    client: testclient.TestClient,
    capella_model: toolmodels_models.DatabaseToolModel,
    capella_tool: tools_models.DatabaseTool,
):
    version = tools_crud.create_version(
        db,
        capella_tool,
        tools_models.CreateToolVersion(
            name="1.0.0", config=tools_models.ToolVersionConfiguration()
        ),
    )

    response = client.patch(
        f"/api/v1/projects/{capella_model.project.slug}/models/{capella_model.slug}",
        json={
            "version_id": version.id,
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "T4C_INTEGRATION_WRONG_CAPELLA_VERSION"
    )


@pytest.fixture
def training_tool(db: orm.Session) -> tools_models.DatabaseTool:
    tool = tools_models.CreateTool(
        name="Training Tool",
        config=tools_models.ToolSessionConfiguration(
            supported_project_types=[projects_models.ProjectType.TRAINING]
        ),
    )

    return tools_crud.create_tool(db, tool)


@pytest.mark.usefixtures("admin")
def test_create_training_toolmodel(
    training_project: projects_models.DatabaseProject,
    client: testclient.TestClient,
    training_tool: tools_models.DatabaseTool,
):
    response = client.post(
        f"/api/v1/projects/{training_project.slug}/models",
        json={
            "name": "Valid Training Toolmodel",
            "description": "",
            "tool_id": training_tool.id,
        },
    )

    assert response.status_code == 200
    assert "Valid Training Toolmodel" in response.text


@pytest.mark.usefixtures("admin")
def test_create_toolmodel_project_type_not_allowed(
    project: projects_models.DatabaseProject,
    client: testclient.TestClient,
    training_tool: tools_models.DatabaseTool,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models",
        json={
            "name": "Invalid Training Toolmodel",
            "description": "",
            "tool_id": training_tool.id,
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "PROJECT_TYPE_NOT_SUPPORTED_BY_TOOLMODEL"
    )
