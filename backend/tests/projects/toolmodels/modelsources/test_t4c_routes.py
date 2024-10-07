# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.models as projects_models
from capellacollab.projects.toolmodels import crud as toolmodels_crud
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.modelsources.t4c import crud as t4c_crud
from capellacollab.projects.toolmodels.modelsources.t4c import (
    models as t4c_models,
)
from capellacollab.settings.modelsources.t4c.instance import (
    crud as t4c_servers_crud,
)
from capellacollab.settings.modelsources.t4c.instance import (
    models as t4c_servers_models,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    crud as t4c_repositories_crud,
)
from capellacollab.settings.modelsources.t4c.instance.repositories import (
    models as t4c_repositories_models,
)
from capellacollab.settings.modelsources.t4c.license_server import (
    models as license_server_models,
)
from capellacollab.tools import models as tools_models


@pytest.mark.usefixtures("project_manager")
def test_list_t4c_models(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_model: t4c_models.DatabaseT4CModel,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == t4c_model.name


@pytest.mark.usefixtures("project_manager")
def test_get_t4c_model(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_model: t4c_models.DatabaseT4CModel,
):
    response = client.get(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c/{t4c_model.id}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == t4c_model.name
    assert (
        response.json()["repository"]["instance"]["id"]
        == t4c_model.repository.instance.id
    )


@pytest.mark.usefixtures("admin")
def test_create_t4c_model(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    t4c_repository: t4c_repositories_models.DatabaseT4CRepository,
    capella_model: toolmodels_models.DatabaseToolModel,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c",
        json={
            "name": "project",
            "t4c_instance_id": t4c_repository.instance.id,
            "t4c_repository_id": t4c_repository.id,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "project"
    assert response.json()["repository"]["id"] == t4c_repository.id
    assert (
        response.json()["repository"]["instance"]["id"]
        == t4c_repository.instance.id
    )


@pytest.mark.usefixtures("admin", "t4c_model")
def test_create_t4c_model_twice_fails(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    t4c_repository: t4c_repositories_models.DatabaseT4CRepository,
    capella_model: toolmodels_models.DatabaseToolModel,
):
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c",
        json={
            "name": "default",
            "t4c_instance_id": t4c_repository.instance.id,
            "t4c_repository_id": t4c_repository.id,
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"]
        == "T4C_INTEGRATION_ALREADY_EXISTS"
    )


@pytest.mark.usefixtures("admin")
def test_create_t4c_model_incompatible_version(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    t4c_repository: t4c_repositories_models.DatabaseT4CRepository,
    capella_tool: tools_models.DatabaseTool,
    db: orm.Session,
    tool_version: tools_models.DatabaseVersion,
):
    model = toolmodels_crud.create_model(
        db,
        project,
        toolmodels_models.PostToolModel(
            name="test", description="test", tool_id=capella_tool.id
        ),
        capella_tool,
        tool_version,
    )
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{model.slug}/modelsources/t4c",
        json={
            "name": "project",
            "t4c_instance_id": t4c_repository.instance.id,
            "t4c_repository_id": t4c_repository.id,
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"]
        == "T4C_INTEGRATION_WRONG_CAPELLA_VERSION"
    )


@pytest.mark.usefixtures("admin")
def test_create_t4c_model_without_version(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    t4c_repository: t4c_repositories_models.DatabaseT4CRepository,
    db: orm.Session,
    capella_tool: tools_models.DatabaseTool,
):
    model = toolmodels_crud.create_model(
        db,
        project,
        toolmodels_models.PostToolModel(
            name="test", description="test", tool_id=capella_tool.id
        ),
        capella_tool,
    )
    response = client.post(
        f"/api/v1/projects/{project.slug}/models/{model.slug}/modelsources/t4c",
        json={
            "name": "project",
            "t4c_instance_id": t4c_repository.instance.id,
            "t4c_repository_id": t4c_repository.id,
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]["err_code"] == "T4C_INTEGRATION_NO_VERSION"
    )


@pytest.mark.usefixtures("admin")
def test_change_server_of_t4c_model(
    db: orm.Session,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_model: t4c_models.DatabaseT4CModel,
    capella_tool_version: tools_models.DatabaseVersion,
    t4c_license_server: license_server_models.DatabaseT4CLicenseServer,
):
    server = t4c_servers_models.DatabaseT4CInstance(
        name="test server 2",
        host="localhost",
        license_server=t4c_license_server,
        rest_api="http://localhost:8080/api/v1.0",
        username="user",
        password="pass",
        protocol=t4c_servers_models.Protocol.tcp,
        version=capella_tool_version,
    )
    db_server = t4c_servers_crud.create_t4c_instance(db, server)

    second_t4c_repository = t4c_repositories_crud.create_t4c_repository(
        db=db, repo_name="test2", instance=db_server
    )

    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c/{t4c_model.id}",
        json={
            "t4c_instance_id": db_server.id,
            "t4c_repository_id": second_t4c_repository.id,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == t4c_model.name
    assert response.json()["repository"]["id"] == second_t4c_repository.id
    assert (
        response.json()["repository"]["instance"]["id"]
        == second_t4c_repository.instance.id
    )


@pytest.mark.usefixtures("admin")
def test_patch_name_of_t4c_model(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_model: t4c_models.DatabaseT4CModel,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c/{t4c_model.id}",
        json={"name": "new_default"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "new_default"
    assert (
        response.json()["repository"]["instance"]["id"]
        == t4c_model.repository.instance.id
    )


@pytest.mark.usefixtures("admin")
def test_unlink_t4c_model(
    db: orm.Session,
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    t4c_model: t4c_models.DatabaseT4CModel,
):
    response = client.delete(
        f"/api/v1/projects/{project.slug}/models/{capella_model.slug}/modelsources/t4c/{t4c_model.id}",
    )

    assert response.status_code == 204
    assert t4c_crud.get_t4c_model_by_id(db, t4c_model.id) is None
