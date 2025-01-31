# SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
# SPDX-License-Identifier: Apache-2.0

import datetime
import json

import pytest
import responses
from fastapi import testclient
from sqlalchemy import orm

from capellacollab.__main__ import app
from capellacollab.permissions import models as permissions_models
from capellacollab.users import models as users_models
from capellacollab.users.tokens import crud as tokens_crud

POST_TOKEN = {
    "expiration_date": str(datetime.date.today()),
    "description": "test_token",
    "source": "test source",
    "scopes": {},
}


@responses.activate
@pytest.mark.usefixtures("user")
def test_create_user_token(client: testclient.TestClient):
    """Test to create a personal access token"""

    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200


@responses.activate
@pytest.mark.usefixtures("user")
def test_get_user_tokens(client: testclient.TestClient):
    """Test to get all personal access tokens of the own user"""

    response = client.get("/api/v1/users/current/tokens")
    assert response.status_code == 200


@responses.activate
def test_use_basic_token(
    unauthenticated_user: users_models.DatabaseUser,
    db: orm.Session,
):
    """Test to use a PAT as authentication against the API"""
    _, password = tokens_crud.create_token(
        db,
        unauthenticated_user,
        scope=permissions_models.GlobalScopes(),
        description="",
        expiration_date=None,
        source="test",
    )

    client = testclient.TestClient(app)
    response = client.get(
        "/api/v1/projects",
        auth=(unauthenticated_user.name, password),
    )

    assert response.status_code == 200


@responses.activate
def test_use_invalid_basic_token(unauthenticated_user: users_models.User):
    """Test that an invalid PAT is declined for authentication against the API"""
    client = testclient.TestClient(app)
    response = client.get(
        "/api/v1/projects",
        auth=(unauthenticated_user.name, "invalid_password"),
    )
    assert response.status_code == 401
    assert response.json()["detail"]["err_code"] == "BASIC_TOKEN_INVALID"


@responses.activate
def test_create_and_revoke_token(
    client: testclient.TestClient, user: users_models.User
):
    """Test revocation of a created PAT"""
    response = client.post("/api/v1/users/current/tokens", json=POST_TOKEN)
    assert response.status_code == 200

    token_id = response.json()["id"]

    response = client.delete(f"/api/v1/users/current/tokens/{token_id}")
    assert response.status_code == 204


@responses.activate
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


def test_updated_token_scope_on_role_change():
    """Test if token scope is updated when a user's role is changed

    When the role or project role of a user changes, the revoked permissions
    of the user should no longer be accepted, even though the token was initially
    created with the revoked permissions.
    """

    # TODO: Implement this test


def test_token_only_valid_for_requested_scopes():
    """Test that a PAT is only valid for the requested scopes"""

    # TODO: Implement this test


def test_token_creation_fails_insufficient_permission():
    """Test that a token creation fails if the user has not the requested scopes"""

    # TODO: Implement this test


def test_token_creation_refused_with_token():
    """Test that a token creation is refused if the user uses a token for authentication

    This is a security measure to prevent extension of the token validity.
    """
    # TODO: Implement this test


def test_token_creation_fails_without_project_access():
    """Test that a token creation fails if the user has no access to the requested project"""
    # TODO: Implement this test
