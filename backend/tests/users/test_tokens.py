# SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
# SPDX-License-Identifier: Apache-2.0

import base64
import json

import fastapi
import pytest
import responses
from fastapi import testclient

from capellacollab.__main__ import app
from capellacollab.core.authentication.basic_auth import HTTPBasicAuth
from capellacollab.users import models as user_models


@responses.activate
@pytest.mark.usefixtures("user")
def test_get_user_token(client: testclient.TestClient):
    response = client.post(
        f"/api/v1/users/current/token", json="my_test_description"
    )
    assert response.status_code == 200


@responses.activate
@pytest.mark.usefixtures("user")
def test_get_user_tokens(client: testclient.TestClient):
    response = client.get(f"/api/v1/users/current/tokens")
    assert response.status_code == 200


@responses.activate
def test_use_basic_token(
    client: testclient.TestClient,
    unauthenticated_user: user_models.User,
    monkeypatch: pytest.MonkeyPatch,
):
    async def basic_passthrough(self, request: fastapi.Request):
        return unauthenticated_user.name, None

    monkeypatch.setattr(HTTPBasicAuth, "__call__", basic_passthrough)
    token_string = unauthenticated_user.name + ":" + "myTestPassword"
    token = base64.b64encode(token_string.encode("ascii"))
    basic_response = client.post(
        f"/api/v1/users/current/token",
        headers={"Authorization": f"basic {token.decode('ascii')}"},
        json="my_test_description2",
    )

    assert basic_response.status_code == 200


@responses.activate
def test_use_wrong_basic_token(unauthenticated_user: user_models.User):
    token_string = unauthenticated_user.name + ":" + "testPassword"
    token = base64.b64encode(token_string.encode("ascii"))
    basic_client = testclient.TestClient(app)
    basic_response = basic_client.post(
        f"/api/v1/users/current/token",
        headers={"Authorization": f"basic {token.decode('ascii')}"},
        json="my_test_description",
    )
    assert basic_response.status_code == 401


@responses.activate
def test_create_and_delete_token(
    client: testclient.TestClient, user: user_models.User
):
    response = client.post(
        f"/api/v1/users/current/token", json="my_test_description"
    )
    assert response.status_code == 200

    response = client.delete(f"/api/v1/users/current/token/1")
    assert response.status_code == 200


@responses.activate
def test_token_lifecycle(
    client: testclient.TestClient, user: user_models.User
):
    response = client.post(
        f"/api/v1/users/current/token", json="my_test_description"
    )
    assert response.status_code == 200

    response = client.get(f"/api/v1/users/current/tokens")
    response_string = response.content.decode("utf-8")
    assert len(json.loads(response_string)) == 1

    response = client.delete(f"/api/v1/users/current/token/1")
    assert response.status_code == 200

    response = client.get(f"/api/v1/users/current/tokens")
    response_string = response.content.decode("utf-8")
    assert len(json.loads(response_string)) == 0
