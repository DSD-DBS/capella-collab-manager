# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import fastapi
import pytest
from fastapi import testclient

from capellacollab.permissions import injectables as permissions_injectables
from capellacollab.permissions import models as permissions_models
from capellacollab.users import models as users_models


def test_get_available_permissions(
    client_unauthenticated: testclient.TestClient,
):
    """Test to get the available global permissions"""
    response = client_unauthenticated.get("/api/v1/permissions")

    assert response.status_code == 200
    assert "$defs" in response.json()


def test_get_actual_permissions(
    client: testclient.TestClient, user: users_models.DatabaseUser
):
    """Test to get the actual global permissions for a user"""
    response = client.get(f"/api/v1/users/{user.id}/permissions")

    assert response.status_code == 200

    # Users should be able to get their own sessions
    assert "GET" in response.json()["user"]["sessions"]

    # "Normal" user should not be able to update tools
    assert not response.json()["admin"]["tools"]


@pytest.mark.usefixtures("admin")
def test_get_actual_permissions_as_admin_for_other_user(
    client: testclient.TestClient,
    user2: users_models.DatabaseUser,
):
    """Test to get the actual global permissions for another user"""
    response = client.get(f"/api/v1/users/{user2.id}/permissions")

    assert response.status_code == 200
    assert "GET" in response.json()["user"]["sessions"]


@pytest.mark.usefixtures("user")
def test_get_actual_permissions_as_user_for_other_user(
    client: testclient.TestClient,
    user2: users_models.DatabaseUser,
):
    """Test to get the actual global permissions for another user"""
    response = client.get(f"/api/v1/users/{user2.id}/permissions")

    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "INSUFFICIENT_PERMISSION"


@pytest.mark.usefixtures("user")
def test_permission_validation_passes(
    client: testclient.TestClient,
):
    """Test that the permission validation passes if permissions are sufficient"""
    response = client.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["user.sessions:get"]},
    )

    assert response.status_code == 204


@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(
                user=permissions_models.UserScopes(
                    sessions={permissions_models.UserTokenVerb.GET}
                )
            ),
            None,
        )
    ],
)
def test_permission_validation_passes_pat(
    client_pat: testclient.TestClient,
):
    """Test that the permission validation passes if token permissions are sufficient"""
    response = client_pat.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["user.sessions:get"]},
    )

    assert response.status_code == 204


@pytest.mark.usefixtures("user")
def test_validate_permission_with_invalid_permission_format(
    client: testclient.TestClient,
):
    """Test that the validate permission route fails with missing verb in the request"""
    response = client.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["user.sessions"]},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["err_code"] == "INVALID_PERMISSION_FORMAT"


@pytest.mark.usefixtures("user")
def test_validate_permission_with_invalid_permission(
    client: testclient.TestClient,
):
    """Test that the validate permission route fails if the permission is invalid"""
    response = client.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["user.sessions2:get"]},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["err_code"] == "PERMISSION_NOT_FOUND"


def test_permission_validation_user_not_found(client: testclient.TestClient):
    """Test that the permission validation fails if the user doesn't exist"""
    response = client.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["user.sessions:get"]},
    )

    assert response.status_code == 404
    assert response.json()["detail"]["err_code"] == "USER_NOT_FOUND"


@pytest.mark.usefixtures("user")
def test_permission_validation_fails_with_insufficient_permission(
    client: testclient.TestClient,
):
    """Test that the permission validation fails if the user has insufficient permissions"""
    response = client.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["admin.tools:create"]},
    )

    assert response.status_code == 403


@pytest.mark.usefixtures("user")
def test_permission_validation_fails_with_insufficient_permission_pat(
    client_pat: testclient.TestClient,
):
    """Test that the permission validation fails if the token has insufficient permissions"""
    response = client_pat.get(
        "/api/v1/permissions/validate",
        params={"required_scopes": ["user.sessions:get"]},
    )

    assert response.status_code == 403


@pytest.mark.usefixtures("admin", "mock_request_logger")
def test_permission_validation_injectable_passes(
    id_token: str,
    mock_router: fastapi.FastAPI,
):
    @mock_router.get(
        "/",
        dependencies=[
            fastapi.Depends(
                permissions_injectables.PermissionValidation(
                    required_scope=permissions_models.GlobalScopes(
                        admin=permissions_models.AdminScopes(
                            sessions={permissions_models.UserTokenVerb.GET}
                        )
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        "/",
        cookies={"id_token": id_token},
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("mock_request_logger")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(
                admin=permissions_models.AdminScopes(
                    sessions={permissions_models.UserTokenVerb.GET}
                )
            ),
            None,
        )
    ],
)
def test_permission_validation_injectable_passes_pat(
    user: users_models.DatabaseUser,
    pat_password: str,
    mock_router: fastapi.FastAPI,
):
    user.role = users_models.Role.ADMIN

    @mock_router.get(
        "/",
        dependencies=[
            fastapi.Depends(
                permissions_injectables.PermissionValidation(
                    required_scope=permissions_models.GlobalScopes(
                        admin=permissions_models.AdminScopes(
                            sessions={permissions_models.UserTokenVerb.GET}
                        )
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        "/",
        auth=(user.name, pat_password),
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("user", "mock_request_logger")
def test_permission_validation_injectable_insufficient_permission(
    id_token: str,
    mock_router: fastapi.FastAPI,
):
    """Test that the permission validation fails if the user has insufficient permissions"""

    @mock_router.get(
        "/",
        dependencies=[
            fastapi.Depends(
                permissions_injectables.PermissionValidation(
                    required_scope=permissions_models.GlobalScopes(
                        admin=permissions_models.AdminScopes(
                            sessions={permissions_models.UserTokenVerb.GET}
                        )
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        "/",
        cookies={"id_token": id_token},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "INSUFFICIENT_PERMISSION"


@pytest.mark.usefixtures("user", "mock_request_logger")
def test_permission_validation_injectable_insufficient_permission_pat(
    user: users_models.DatabaseUser,
    pat_password: str,
    mock_router: fastapi.FastAPI,
):
    """Test that the permission validation fails if the user has insufficient permissions"""
    user.role = users_models.Role.ADMIN

    @mock_router.get(
        "/",
        dependencies=[
            fastapi.Depends(
                permissions_injectables.PermissionValidation(
                    required_scope=permissions_models.GlobalScopes(
                        admin=permissions_models.AdminScopes(
                            sessions={permissions_models.UserTokenVerb.GET}
                        )
                    )
                )
            )
        ],
    )
    def test_route():
        pass

    client = testclient.TestClient(mock_router)
    response = client.get(
        "/",
        auth=(user.name, pat_password),
    )
    assert response.status_code == 403
    assert response.json()["detail"]["err_code"] == "INSUFFICIENT_PERMISSION"


def test_global_scope_merging():
    assert permissions_models.GlobalScopes(
        admin=permissions_models.AdminScopes(
            users={
                permissions_models.UserTokenVerb.GET,
                permissions_models.UserTokenVerb.CREATE,
            }
        )
    ) & permissions_models.GlobalScopes(
        admin=permissions_models.AdminScopes(
            users={
                permissions_models.UserTokenVerb.GET,
                permissions_models.UserTokenVerb.UPDATE,
            }
        ),
        user=permissions_models.UserScopes(
            sessions={permissions_models.UserTokenVerb.GET}
        ),
    ) == permissions_models.GlobalScopes(
        admin=permissions_models.AdminScopes(
            users={
                permissions_models.UserTokenVerb.GET,
            }
        ),
    )

    assert permissions_models.GlobalScopes(
        admin=permissions_models.AdminScopes(
            users={
                permissions_models.UserTokenVerb.GET,
                permissions_models.UserTokenVerb.CREATE,
            }
        )
    ) | permissions_models.GlobalScopes(
        admin=permissions_models.AdminScopes(
            users={
                permissions_models.UserTokenVerb.GET,
                permissions_models.UserTokenVerb.UPDATE,
            }
        ),
        user=permissions_models.UserScopes(
            sessions={permissions_models.UserTokenVerb.GET}
        ),
    ) == permissions_models.GlobalScopes(
        admin=permissions_models.AdminScopes(
            users={
                permissions_models.UserTokenVerb.GET,
                permissions_models.UserTokenVerb.CREATE,
                permissions_models.UserTokenVerb.UPDATE,
            }
        ),
        user=permissions_models.UserScopes(
            sessions={permissions_models.UserTokenVerb.GET}
        ),
    )

    with pytest.raises(TypeError):
        permissions_models.GlobalScopes() & None  # type: ignore

    with pytest.raises(TypeError):
        permissions_models.GlobalScopes() | None  # type: ignore
