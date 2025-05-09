# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0


from unittest import mock

import pytest
from fastapi import testclient
from sqlalchemy import orm

import capellacollab.projects.crud as projects_crud
import capellacollab.projects.models as projects_models
import capellacollab.projects.users.crud as projects_users_crud
import capellacollab.projects.users.models as projects_users_models
import capellacollab.users.models as users_models
from capellacollab.permissions import models as permissions_models
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.toolmodels import models as toolmodels_models
from capellacollab.projects.toolmodels.backups import (
    models as pipelines_models,
)
from capellacollab.tags import crud as tags_crud
from capellacollab.tags import models as tags_models


@pytest.mark.usefixtures("user")
def test_get_internal_default_project_as_user(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/melody-model-test")

    assert response.status_code == 200
    assert response.json()["name"] == "Melody Model Test"
    assert response.json()["visibility"] == "internal"
    assert response.json()["slug"] == "melody-model-test"


@pytest.mark.usefixtures("user")
def test_get_projects_as_user_only_shows_default_internal_project(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    for project in data:
        assert project["visibility"] == "internal"


@pytest.mark.usefixtures("project_manager")
def test_get_projects_as_user_with_project(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
):
    """Test that a user can see their private projects"""

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "private"


@pytest.mark.usefixtures("admin")
def test_get_projects_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
):
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.PRIVATE,
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "private"


@pytest.mark.usefixtures("user")
def test_get_internal_projects_as_user(
    client: testclient.TestClient,
    db: orm.Session,
):
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.INTERNAL,
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0
    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "internal"


def test_get_internal_projects_as_user_without_duplicates(
    client: testclient.TestClient,
    db: orm.Session,
    user: users_models.DatabaseUser,
):
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.INTERNAL,
    )
    projects_users_crud.add_user_to_project(
        db,
        project,
        user,
        projects_users_models.ProjectUserRole.USER,
        projects_users_models.ProjectUserPermission.WRITE,
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 1

    assert data[0]["slug"] == "melody-model-test"
    assert data[0]["visibility"] == "internal"
    assert data[0]["users"]["contributors"] == 0

    assert data[-1]["slug"] == project.slug
    assert data[-1]["visibility"] == "internal"
    assert data[-1]["users"]["contributors"] == 1


@pytest.mark.usefixtures("admin")
def test_create_private_project_as_admin(
    client: testclient.TestClient,
):
    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == "test-project"
    assert data["visibility"] == "private"


@pytest.mark.usefixtures("admin")
def test_create_internal_project_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
):
    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == "test-project"
    assert data["visibility"] == "internal"


@pytest.mark.usefixtures("admin")
def test_create_project_name_already_taken(
    client: testclient.TestClient,
    db: orm.Session,
):
    project = projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.INTERNAL,
    )
    projects_crud.update_project(
        db,
        project,
        projects_models.PatchProject(
            name="test project 2",
        ),
    )

    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project 2",
            "description": "",
            "visibility": "internal",
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"] == "PROJECT_NAME_ALREADY_EXISTS"
    )


@pytest.mark.usefixtures("admin")
def test_create_project_slug_already_taken(
    client: testclient.TestClient,
    db: orm.Session,
):
    projects_crud.create_project(
        db,
        "test project",
        visibility=projects_models.ProjectVisibility.INTERNAL,
    )

    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["err_code"] == "PROJECT_ALREADY_EXISTS"


@pytest.mark.usefixtures("admin")
def test_update_project_as_admin(
    client: testclient.TestClient,
    db: orm.Session,
):
    project = projects_crud.create_project(db, "new project")

    assert project.slug == "new-project"
    assert project.visibility == projects_models.ProjectVisibility.PRIVATE
    assert project.is_archived is False

    response = client.patch(
        "/api/v1/projects/new-project",
        json={
            "name": "test project",
            "description": "",
            "visibility": "internal",
            "is_archived": "true",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "test project"
    assert data["slug"] == "new-project"
    assert data["visibility"] == "internal"
    assert data["is_archived"]


@pytest.mark.usefixtures("admin")
def test_add_tags_to_project(
    client: testclient.TestClient,
    tag: tags_models.DatabaseTag,
    db: orm.Session,
    project: projects_models.DatabaseProject,
):
    tag2 = tags_crud.create_tag(
        db, tags_models.CreateTag(name="tag2", hex_color="#FF5733")
    )
    response = client.patch(
        f"/api/v1/projects/{project.slug}",
        json={"tags": [tag.name, tag2.id]},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["tags"]) == 2
    assert data["tags"][0]["id"] == tag.id
    assert data["tags"][1]["id"] == tag2.id


@pytest.mark.usefixtures("admin")
def test_add_same_tag_to_project_twice(
    client: testclient.TestClient,
    tag: tags_models.DatabaseTag,
    project: projects_models.DatabaseProject,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}",
        json={"tags": [tag.name, tag.id]},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["tags"]) == 1
    assert data["tags"][0]["id"] == tag.id


@pytest.mark.usefixtures("admin")
def test_add_non_existing_tag_to_project(
    client: testclient.TestClient,
    tag: tags_models.DatabaseTag,
    project: projects_models.DatabaseProject,
):
    response = client.patch(
        f"/api/v1/projects/{project.slug}",
        json={"tags": ["unknown tag"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "TAG_NOT_FOUND"


@pytest.mark.usefixtures("admin")
def test_remove_tag_from_project(
    client: testclient.TestClient,
    tag: tags_models.DatabaseTag,
    project: projects_models.DatabaseProject,
):
    project.tags = [tag]
    response = client.patch(
        f"/api/v1/projects/{project.slug}",
        json={"tags": []},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["tags"]) == 0


@pytest.mark.usefixtures("admin")
def test_update_project_name_already_taken(
    client: testclient.TestClient,
    db: orm.Session,
):
    project = projects_crud.create_project(db, "new project")
    project2 = projects_crud.create_project(db, "new project 2")

    assert project.slug == "new-project"

    response = client.patch(
        f"/api/v1/projects/{project.slug}",
        json={
            "name": project2.name,
        },
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"]["err_code"] == "PROJECT_NAME_ALREADY_EXISTS"
    )


@pytest.mark.parametrize(
    ("run_nightly", "include_commit_history"), [(True, True)]
)
@pytest.mark.usefixtures("admin")
def test_delete_pipeline_called_when_archiving_project(
    client: testclient.TestClient,
    db: orm.Session,
    project: projects_models.DatabaseProject,
    capella_model: toolmodels_models.DatabaseToolModel,
    pipeline: pipelines_models.DatabaseBackup,
):
    with (
        mock.patch(
            "capellacollab.projects.routes.backups_core.delete_pipeline",
            autospec=True,
        ) as mock_delete_pipeline,
        mock.patch(
            "capellacollab.projects.routes.backups_crud.get_pipelines_for_tool_model",
            autospec=True,
        ) as mock_get_pipelines_for_tool_model,
    ):
        mock_get_pipelines_for_tool_model.return_value = [pipeline]

        response = client.patch(
            f"/api/v1/projects/{project.slug}", json={"is_archived": "true"}
        )

        assert response.status_code == 200
        mock_get_pipelines_for_tool_model.assert_called_once_with(
            db, capella_model
        )
        mock_delete_pipeline.assert_called_once_with(
            db,
            pipeline,
            True,
            mock.ANY,
        )


@pytest.mark.usefixtures("project_user")
def test_get_project_per_role_user(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=user")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.usefixtures("project_user")
def test_get_project_per_role_manager_as_user(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=manager")
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.usefixtures("project_manager")
def test_get_project_per_role_manager(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=manager")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.usefixtures("admin")
def test_get_project_per_role_admin(
    client: testclient.TestClient,
):
    response = client.get("/api/v1/projects/?minimum_role=administrator")
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.usefixtures("project_user")
def test_dont_return_project_without_pat_access(
    client_pat: testclient.TestClient, project: projects_models.DatabaseProject
):
    """Test that a project without PAT scope isn't returned"""

    response = client_pat.get("/api/v1/projects")

    assert response.status_code == 200
    assert project.slug not in [project["slug"] for project in response.json()]


@pytest.mark.usefixtures("project_user")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            None,
            projects_permissions_models.ProjectUserScopes(
                root={permissions_models.UserTokenVerb.GET}
            ),
        )
    ],
)
def test_return_project_with_pat_access(
    client_pat: testclient.TestClient, project: projects_models.DatabaseProject
):
    """Test that a project with PAT scope is returned"""

    response = client_pat.get("/api/v1/projects")

    assert response.status_code == 200
    assert project.slug in [project["slug"] for project in response.json()]
