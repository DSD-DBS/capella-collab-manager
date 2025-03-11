# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pytest
from fastapi import testclient

from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    injectables as projects_permissions_injectables,
)
from capellacollab.projects.permissions import (
    models as projects_permissions_models,
)
from capellacollab.projects.users import models as projects_users_models
from capellacollab.users import models as users_models
from capellacollab.users.tokens import models as tokens_models


def test_get_available_project_permissions(
    client_unauthenticated: testclient.TestClient,
):
    """Test to get the available project permissions"""
    response = client_unauthenticated.get("/api/v1/projects/-/permissions")

    assert response.status_code == 200
    assert "properties" in response.json()


@pytest.mark.usefixtures("user", "project_user", "mock_request_logger")
def test_project_permission_validation_injectable_fails_with_insufficient_permission(
    id_token: str,
    project: projects_models.DatabaseProject,
    mock_router: fastapi.APIRouter,
):
    """Test that the project permission validation fails if the user has insufficient permissions"""

    @mock_router.get(
        "/{project_slug}",
        dependencies=[
            fastapi.Depends(
                projects_permissions_injectables.ProjectPermissionValidation(
                    required_scope=projects_permissions_models.ProjectUserScopes(
                        root={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        f"/{project.slug}",
        cookies={"id_token": id_token},
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"]
        == "INSUFFICIENT_PROJECT_PERMISSION"
    )


@pytest.mark.usefixtures("user", "mock_request_logger")
def test_project_permission_validation_injectable_passes(
    id_token: str,
    project: projects_models.DatabaseProject,
    project_user: projects_users_models.DatabaseProjectUserAssociation,
    mock_router: fastapi.APIRouter,
):
    """Test that the project permission validation passes if permissions are sufficient"""
    project_user.role = projects_users_models.ProjectUserRole.MANAGER

    @mock_router.get(
        "/{project_slug}",
        dependencies=[
            fastapi.Depends(
                projects_permissions_injectables.ProjectPermissionValidation(
                    required_scope=projects_permissions_models.ProjectUserScopes(
                        root={permissions_models.UserTokenVerb.UPDATE}
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        f"/{project.slug}",
        cookies={"id_token": id_token},
    )

    assert response.status_code == 200


@pytest.mark.usefixtures("user", "project_user", "mock_request_logger")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(),
            projects_permissions_models.ProjectUserScopes(),
        )
    ],
)
def test_project_permission_validation_injectable_fails_with_insufficient_permission_pat(
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    pat: tuple[tokens_models.DatabaseUserToken, str],
    mock_router: fastapi.APIRouter,
):
    """Test that the project permission validation fails if the user has insufficient permissions of the PAT"""

    @mock_router.get(
        "/{project_slug}",
        dependencies=[
            fastapi.Depends(
                projects_permissions_injectables.ProjectPermissionValidation(
                    required_scope=projects_permissions_models.ProjectUserScopes(
                        root={permissions_models.UserTokenVerb.GET}
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        f"/{project.slug}",
        auth=(user.name, pat[1]),
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]["err_code"]
        == "INSUFFICIENT_PROJECT_PERMISSION"
    )


@pytest.mark.usefixtures("user", "project_user", "mock_request_logger")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(),
            projects_permissions_models.ProjectUserScopes(
                root={permissions_models.UserTokenVerb.GET}
            ),
        )
    ],
)
def test_project_permission_validation_injectable_passes_pat(
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    pat: tuple[tokens_models.DatabaseUserToken, str],
    mock_router: fastapi.APIRouter,
):
    """Test that the project permission validation passes if PAT permissions are sufficient"""

    @mock_router.get(
        "/{project_slug}",
        dependencies=[
            fastapi.Depends(
                projects_permissions_injectables.ProjectPermissionValidation(
                    required_scope=projects_permissions_models.ProjectUserScopes(
                        root={permissions_models.UserTokenVerb.GET}
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        f"/{project.slug}",
        auth=(user.name, pat[1]),
    )

    assert response.status_code == 200


@pytest.mark.usefixtures("admin", "mock_request_logger")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(
                admin=permissions_models.AdminScopes(
                    projects={permissions_models.UserTokenVerb.GET}
                )
            ),
            projects_permissions_models.ProjectUserScopes(),
        )
    ],
)
def test_project_permission_validation_injectable_passes_admin_pat(
    project: projects_models.DatabaseProject,
    user: users_models.DatabaseUser,
    pat: tuple[tokens_models.DatabaseUserToken, str],
    mock_router: fastapi.APIRouter,
):
    """Test that the project permission validation passes with `admin.projects:get` permission"""

    @mock_router.get(
        "/{project_slug}",
        dependencies=[
            fastapi.Depends(
                projects_permissions_injectables.ProjectPermissionValidation(
                    required_scope=projects_permissions_models.ProjectUserScopes(
                        root={permissions_models.UserTokenVerb.GET}
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        f"/{project.slug}",
        auth=(user.name, pat[1]),
    )

    assert response.status_code == 200


def test_project_scope_merging():
    assert projects_permissions_models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
        }
    ) & projects_permissions_models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.DELETE,
        },
        tool_models={
            permissions_models.UserTokenVerb.GET,
        },
    ) == projects_permissions_models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.GET,
        },
    )

    assert projects_permissions_models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
        }
    ) | projects_permissions_models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.DELETE,
        },
        tool_models={
            permissions_models.UserTokenVerb.GET,
        },
    ) == projects_permissions_models.ProjectUserScopes(
        root={
            permissions_models.UserTokenVerb.GET,
            permissions_models.UserTokenVerb.UPDATE,
            permissions_models.UserTokenVerb.DELETE,
        },
        tool_models={
            permissions_models.UserTokenVerb.GET,
        },
    )

    with pytest.raises(TypeError):
        projects_permissions_models.ProjectUserScopes() & None  # type: ignore

    with pytest.raises(TypeError):
        projects_permissions_models.ProjectUserScopes() | None  # type: ignore


@pytest.mark.usefixtures("project_user")
def test_get_actual_project_permissions(
    client: testclient.TestClient,
    user: users_models.DatabaseUser,
    project: projects_models.DatabaseProject,
):
    """Test to get the actual project permissions for a user"""
    response = client.get(
        f"/api/v1/projects/{project.slug}/users/{user.id}/permissions"
    )

    assert response.status_code == 200

    assert "GET" in response.json()["root"]
    assert "UPDATE" not in response.json()["root"]


def test_get_actual_project_permissions_internal_project(
    client: testclient.TestClient,
    user: users_models.DatabaseUser,
):
    """Test to get the actual project permissions for an internal project"""
    response = client.get(
        f"/api/v1/projects/coffee-machine/users/{user.id}/permissions"
    )

    assert response.status_code == 200

    assert "GET" in response.json()["root"]
    assert "UPDATE" not in response.json()["root"]


@pytest.mark.usefixtures("admin")
def test_get_actual_project_permissions_as_admin_for_other_user(
    client: testclient.TestClient,
    user2: users_models.DatabaseUser,
):
    """Test to get the actual project permissions for another user"""
    response = client.get(
        f"/api/v1/projects/coffee-machine/users/{user2.id}/permissions"
    )

    assert response.status_code == 200
    assert "GET" in response.json()["root"]


@pytest.mark.usefixtures("user")
def test_get_actual_project_permissions_as_user_for_other_user(
    client: testclient.TestClient,
    user2: users_models.DatabaseUser,
):
    """Test to get the actual project permissions for another user"""
    response = client.get(
        f"/api/v1/projects/coffee-machine/users/{user2.id}/permissions"
    )

    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "INSUFFICIENT_PERMISSION"
