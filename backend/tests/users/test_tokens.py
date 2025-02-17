# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import json

import pytest
from fastapi import testclient

from capellacollab.__main__ import app
from capellacollab.permissions import models as permissions_models
from capellacollab.projects import models as projects_models
from capellacollab.projects.permissions import (
    models as project_permissions_models,
)
from capellacollab.projects.users import models as project_users_models
from capellacollab.users import models as users_models

POST_TOKEN = {
    "expiration_date": str(datetime.datetime.now(tz=datetime.UTC).date()),
    "title": "test",
    "description": "test_token",
    "source": "test source",
    "scopes": {},
}


@pytest.mark.usefixtures("user")
def test_create_pat(client: testclient.TestClient):
    """Test to create a personal access token"""

    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200


@pytest.mark.usefixtures("user")
def test_create_pat_with_scope(client: testclient.TestClient):
    """Test to create a personal access token"""

    response = client.post(
        "/api/v1/users/current/tokens",
        json={
            "expiration_date": str(
                datetime.datetime.now(tz=datetime.UTC).date()
            ),
            "title": "test",
            "description": "test_token",
            "source": "test source",
            "scopes": {
                "projects": {"coffee-machine": {"root": ["UPDATE"]}},
                "user": {"sessions": ["GET"]},
            },
        },
    )
    assert response.status_code == 200
    assert response.json()["requested_scopes"]["projects"]["coffee-machine"][
        "root"
    ] == ["UPDATE"]
    assert response.json()["requested_scopes"]["user"]["sessions"] == ["GET"]


@pytest.mark.usefixtures("user")
def test_get_pat_of_user(client: testclient.TestClient):
    """Test to get all personal access tokens of the own user"""

    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200


def test_use_pat(
    client_pat: testclient.TestClient,
):
    """Test to use a PAT as authentication against the API"""
    response = client_pat.get(
        "/api/v1/projects",
    )

    assert response.status_code == 200


def test_use_invalid_pat(unauthenticated_user: users_models.User):
    """Test that an invalid PAT is declined for authentication against the API"""
    client = testclient.TestClient(app)
    response = client.get(
        "/api/v1/projects",
        auth=(unauthenticated_user.name, "invalid_password"),
    )
    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "BASIC_TOKEN_INVALID"


def test_create_and_revoke_token(
    client: testclient.TestClient, user: users_models.User
):
    """Test revocation of a created PAT"""
    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200

    token_id = response.json()["id"]

    response = client.delete(f"/api/v1/users/current/tokens/{token_id}")
    assert response.status_code == 204


def test_token_lifecycle(
    client: testclient.TestClient, user: users_models.User
):
    """Test the lifecycle of a PAT (create, get, revoke, get)"""
    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200

    response = client.get("/api/v1/users/current/tokens")
    response_string = response.content.decode("utf-8")
    assert len(json.loads(response_string)) == 1

    token_id = response.json()[0]["id"]

    response = client.delete(f"/api/v1/users/current/tokens/{token_id}")
    assert response.status_code == 204

    response = client.get("/api/v1/users/current/tokens")
    response_string = response.content.decode("utf-8")
    assert len(json.loads(response_string)) == 0


@pytest.mark.usefixtures("pat")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(
                admin=permissions_models.AdminScopes(
                    users={permissions_models.UserTokenVerb.GET}
                )
            ),
            None,
        )
    ],
)
def test_updated_token_scope_on_role_change(
    client: testclient.TestClient, user: users_models.User
):
    """Test if token scope is updated when a user's role is changed

    When the role or project role of a user changes, the revoked permissions
    of the user should no longer be accepted, even though the token was initially
    created with the revoked permissions.
    """

    user.role = users_models.Role.ADMIN

    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["requested_scopes"]["admin"]["users"] == ["GET"]
    assert response.json()[0]["actual_scopes"]["admin"]["users"] == ["GET"]

    user.role = users_models.Role.USER

    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["requested_scopes"]["admin"]["users"] == ["GET"]
    assert response.json()[0]["actual_scopes"]["admin"]["users"] == []


@pytest.mark.usefixtures("pat")
@pytest.mark.parametrize(
    "pat_scope",
    [
        (
            permissions_models.GlobalScopes(),
            project_permissions_models.ProjectUserScopes(
                root={permissions_models.UserTokenVerb.UPDATE}
            ),
        )
    ],
)
def test_updated_token_scope_on_project_role_change(
    client: testclient.TestClient,
    project: projects_models.DatabaseProject,
    project_user: project_users_models.DatabaseProjectUserAssociation,
):
    project_user.role = project_users_models.ProjectUserRole.MANAGER

    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["requested_scopes"]["projects"][project.slug][
        "root"
    ] == ["UPDATE"]
    assert response.json()[0]["actual_scopes"]["projects"][project.slug][
        "root"
    ] == ["UPDATE"]

    project_user.role = project_users_models.ProjectUserRole.USER

    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["requested_scopes"]["projects"][project.slug][
        "root"
    ] == ["UPDATE"]
    assert (
        response.json()[0]["actual_scopes"]["projects"][project.slug]["root"]
        == []
    )
